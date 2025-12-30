import os
import sys
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import socketio

# Permit imports dos módulos do pacote pocket_robot
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from connection_monitor import ConnectionMonitor
import constants

POCKET_SSID = os.environ.get('POCKET_SSID') or os.environ.get('POCKET_SSID_OVERRIDE') or constants.CONFIGURED_SSID

# Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()

# Mount frontend static files
frontend_dir = os.path.join(ROOT, 'frontend')
if not os.path.isdir(frontend_dir):
    os.makedirs(frontend_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=frontend_dir), name="frontend")

# Serve index.html at root
@app.get('/')
def root_index():
    index_path = os.path.join(frontend_dir, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail='index.html not found')

# Global robot, subscriptions and background task
robot = None
market_broadcaster_task = None
# subscriptions: sid -> set(symbols)
subscriptions = {}

# admin token for secure config actions
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', None)


@app.on_event('startup')
async def startup_event():
    # nothing special yet
    pass


@app.get('/api/assets')
def get_assets():
    return JSONResponse(constants.ACTIVES)


@app.post('/api/start')
async def api_start():
    global robot, market_broadcaster_task
    if robot and robot.is_running:
        return {'status': 'already_running'}

    robot = None
    robot = __import__('main').PocketOptionRobot()
    # use env SSID
    if POCKET_SSID:
        robot.ssid = POCKET_SSID

    loop = asyncio.get_event_loop()
    loop.create_task(robot.start_monitoring())

    # start broadcaster
    if market_broadcaster_task is None:
        market_broadcaster_task = loop.create_task(broadcaster_loop())

    return {'status': 'started'}


@app.post('/api/stop')
async def api_stop():
    global robot
    if not robot:
        return {'status': 'not_running'}
    await robot.stop_monitoring()
    return {'status': 'stopped'}


@app.post('/api/config')
async def api_config(body: dict, x_admin_token: str = None):
    """Update runtime configuration (e.g., POCKET_SSID). Requires ADMIN_TOKEN if set."""
    global POCKET_SSID
    if ADMIN_TOKEN:
        token = body.get('admin_token') or x_admin_token
        if token != ADMIN_TOKEN:
            raise HTTPException(status_code=403, detail='invalid admin token')

    ssid = body.get('pocket_ssid')
    if ssid:
        POCKET_SSID = ssid
        # if robot exists, update its ssid (will take effect on next start)
        if robot:
            robot.ssid = ssid
        return {'status': 'ok', 'pocket_ssid': ssid}

    raise HTTPException(status_code=400, detail='pocket_ssid required')


@app.get('/api/perf')
def api_perf():
    if not robot:
        return {'status': 'not_running'}
    return JSONResponse(robot.get_performance_summary())


@sio.event
async def connect(sid, environ, auth):
    await sio.emit('server_msg', {'msg': 'connected'}, to=sid)


@sio.event
async def disconnect(sid):
    pass


@sio.event
async def ping_check(sid):
    await sio.emit('pong', {}, to=sid)


@sio.event
async def subscribe(sid, data):
    """Client sends list of symbols to subscribe to: { symbols: [...] }"""
    try:
        syms = data.get('symbols') if isinstance(data, dict) else data
        if not syms:
            subscriptions.pop(sid, None)
            return
        subscriptions[sid] = set(syms)
    except Exception:
        subscriptions.pop(sid, None)


@sio.event
async def unsubscribe(sid, data):
    subscriptions.pop(sid, None)


async def broadcaster_loop():
    global robot
    try:
        while True:
            if robot and robot.market_data:
                # For each connected client, emit only subscribed symbols
                for sid, syms in list(subscriptions.items()):
                    try:
                        payload = []
                        # limit to existing symbols
                        for symbol in list(syms)[:200]:
                            md = robot.market_data.get(symbol)
                            if md:
                                payload.append({'symbol': symbol, 'price': md.current_price})
                        await sio.emit('tick', payload, to=sid)
                    except Exception:
                        pass

                # Broadcast performance once to all
                await sio.emit('perf', robot.get_performance_summary())
            else:
                # if no robot, send empty ticks to subscribed clients
                for sid in list(subscriptions.keys()):
                    await sio.emit('tick', [], to=sid)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        return


# Combine FastAPI app and Socket.IO ASGI app
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(asgi_app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))

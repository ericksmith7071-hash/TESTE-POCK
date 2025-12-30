"""
Advanced Connection Monitor and Diagnostics Tool
Real-time monitoring, diagnostics, and performance analysis
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import statistics
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConnectionMetrics:
    """Connection performance metrics"""
    timestamp: datetime
    connection_time: float
    ping_time: Optional[float]
    message_count: int
    error_count: int
    region: str
    status: str

@dataclass
class PerformanceSnapshot:
    """Performance snapshot"""
    timestamp: datetime
    memory_usage_mb: float
    cpu_percent: float
    active_connections: int
    messages_per_second: float
    error_rate: float
    avg_response_time: float

class MockPocketOptionClient:
    """Cliente mock para simulação"""
    def __init__(self, ssid, is_demo=True, **kwargs):
        self.ssid = ssid
        self.is_demo = is_demo
        self.is_connected = False
        self.connection_info = None
        self.event_callbacks = defaultdict(list)
        
    async def connect(self):
        """Simula conexão"""
        await asyncio.sleep(1)
        self.is_connected = True
        return True
        
    async def disconnect(self):
        """Simula desconexão"""
        self.is_connected = False
        
    async def get_balance(self):
        """Simula obtenção de saldo"""
        if self.is_connected:
            return {"balance": 10000.0, "currency": "USD"}
        return None
        
    async def send_message(self, message):
        """Simula envio de mensagem"""
        await asyncio.sleep(0.01)
        return True
        
    def add_event_callback(self, event_type, callback):
        """Adiciona callback de evento"""
        self.event_callbacks[event_type].append(callback)


class RealPocketOptionClient:
    """Cliente Socket.IO real para conectar à Pocket Option (apenas leitura/monitoramento)."""
    def __init__(self, ssid, is_demo=True, region_urls=None, **kwargs):
        import socketio
        self.ssid = ssid
        self.is_demo = is_demo
        self.is_connected = False
        self.event_callbacks = defaultdict(list)
        self.sio = socketio.AsyncClient(reconnection=True, logger=False)
        self._task = None

        # escolher endpoints
        self.region_urls = region_urls

        # registrar handlers
        @self.sio.event
        async def connect():
            self.is_connected = True
            await self._emit_event('connected', {'ssid': self.ssid})

        @self.sio.event
        async def disconnect():
            self.is_connected = False
            await self._emit_event('disconnected', {})

        @self.sio.on('tick')
        async def on_tick(data):
            await self._emit_event('tick', data)

        @self.sio.on('balance')
        async def on_balance(data):
            await self._emit_event('balance', data)

        @self.sio.on('error')
        async def on_error(data):
            await self._emit_event('error', data)

    async def connect(self):
        """Conecta ao primeiro endpoint disponível."""
        try:
            urls = list(self.region_urls) if self.region_urls else []
            if not urls:
                # fallback para demo region do constants
                from constants import REGION
                urls = REGION.get_demo_regions()

            # tenta conectar nas urls até conseguir
            for url in urls:
                try:
                    await self.sio.connect(url, transports=['websocket'], auth={'token': self.ssid})
                    self.is_connected = True
                    return True
                except Exception:
                    continue

            return False
        except Exception as e:
            return False

    async def disconnect(self):
        try:
            await self.sio.disconnect()
        finally:
            self.is_connected = False

    async def get_balance(self):
        # se o servidor suportar um evento de requisição de balance, podemos implementar
        return None

    async def send_message(self, message):
        try:
            await self.sio.emit('42["ps"]', message)
            return True
        except Exception:
            return False

    def add_event_callback(self, event_type, callback):
        self.event_callbacks[event_type].append(callback)

    async def _emit_event(self, event_type, data):
        if event_type in self.event_callbacks:
            for handler in self.event_callbacks[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception:
                    pass

class ConnectionMonitor:
    """Advanced connection monitoring and diagnostics"""

    def __init__(self, ssid: str, is_demo: bool = True):
        self.ssid = ssid
        self.is_demo = is_demo

        # Monitoring state
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.client: Optional[MockPocketOptionClient] = None

        # Metrics storage
        self.connection_metrics: deque = deque(maxlen=1000)
        self.performance_snapshots: deque = deque(maxlen=500)
        self.error_log: deque = deque(maxlen=200)
        self.message_stats: Dict[str, int] = defaultdict(int)

        # Real-time stats
        self.start_time = datetime.now()
        self.total_messages = 0
        self.total_errors = 0
        self.last_ping_time = None
        self.ping_times: deque = deque(maxlen=100)

        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Performance tracking
        self.response_times: deque = deque(maxlen=100)
        self.connection_attempts = 0
        self.successful_connections = 0

    async def start_monitoring(self, persistent_connection: bool = True) -> bool:
        """Start real-time monitoring"""
        logger.info("Iniciando monitoramento de conexão...")

        try:
            # Initialize client: use real client if POCKET_USE_REAL env set
            use_real = False
            try:
                import os
                use_real = os.environ.get('POCKET_USE_REAL', '1') == '1'
            except Exception:
                use_real = False

            if use_real:
                try:
                    self.client = RealPocketOptionClient(self.ssid, is_demo=self.is_demo, region_urls=None)
                except Exception:
                    self.client = MockPocketOptionClient(self.ssid, is_demo=self.is_demo)
            else:
                self.client = MockPocketOptionClient(self.ssid, is_demo=self.is_demo)

            # Setup event handlers
            self._setup_event_handlers()

            # Connect
            self.connection_attempts += 1
            start_time = time.time()

            success = await self.client.connect()

            if success:
                connection_time = time.time() - start_time
                self.successful_connections += 1

                # Record connection metrics
                self._record_connection_metrics(connection_time, "CONNECTED")

                # Start monitoring tasks
                self.is_monitoring = True
                self.monitor_task = asyncio.create_task(self._monitoring_loop())

                logger.info(f"Monitoramento iniciado (tempo de conexão: {connection_time:.3f}s)")
                return True
            else:
                self._record_connection_metrics(0, "FAILED")
                logger.error("Falha ao conectar para monitoramento")
                return False

        except Exception as e:
            self.total_errors += 1
            self._record_error("monitoring_start", str(e))
            logger.error(f"Falha ao iniciar monitoramento: {e}")
            return False

    async def stop_monitoring(self):
        """Stop monitoring"""
        logger.info("Parando monitoramento de conexão...")

        self.is_monitoring = False

        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        if self.client:
            await self.client.disconnect()

        logger.info("Monitoramento parado")

    def _setup_event_handlers(self):
        """Setup event handlers for monitoring"""
        if not self.client:
            return

        # Connection events
        self.client.add_event_callback("connected", self._on_connected)
        self.client.add_event_callback("disconnected", self._on_disconnected)
        self.client.add_event_callback("reconnected", self._on_reconnected)
        self.client.add_event_callback("auth_error", self._on_auth_error)

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Iniciando loop de monitoramento...")

        while self.is_monitoring:
            try:
                # Collect performance snapshot
                await self._collect_performance_snapshot()

                # Check connection health
                await self._check_connection_health()

                # Send ping and measure response
                await self._measure_ping_response()

                # Emit monitoring events
                await self._emit_monitoring_events()

                await asyncio.sleep(5)  # Monitor every 5 seconds

            except Exception as e:
                self.total_errors += 1
                self._record_error("monitoring_loop", str(e))
                logger.error(f"Erro no loop de monitoramento: {e}")

    async def _collect_performance_snapshot(self):
        """Collect performance metrics snapshot"""
        try:
            # Try to get system metrics
            memory_mb = 0
            cpu_percent = 0

            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()
            except ImportError:
                pass

            # Calculate messages per second
            uptime = (datetime.now() - self.start_time).total_seconds()
            messages_per_second = self.total_messages / uptime if uptime > 0 else 0

            # Calculate error rate
            error_rate = self.total_errors / max(self.total_messages, 1)

            # Calculate average response time
            avg_response_time = (
                statistics.mean(self.response_times) if self.response_times else 0
            )

            snapshot = PerformanceSnapshot(
                timestamp=datetime.now(),
                memory_usage_mb=memory_mb,
                cpu_percent=cpu_percent,
                active_connections=1 if self.client and self.client.is_connected else 0,
                messages_per_second=messages_per_second,
                error_rate=error_rate,
                avg_response_time=avg_response_time,
            )

            self.performance_snapshots.append(snapshot)

        except Exception as e:
            logger.error(f"Erro coletando snapshot de performance: {e}")

    async def _check_connection_health(self):
        """Check connection health status"""
        if not self.client:
            return

        try:
            # Check if still connected
            if not self.client.is_connected:
                self._record_connection_metrics(0, "DISCONNECTED")
                return

            # Try to get balance as health check
            start_time = time.time()
            balance = await self.client.get_balance()
            response_time = time.time() - start_time

            self.response_times.append(response_time)

            if balance:
                self._record_connection_metrics(response_time, "HEALTHY")
            else:
                self._record_connection_metrics(response_time, "UNHEALTHY")

        except Exception as e:
            self.total_errors += 1
            self._record_error("health_check", str(e))
            self._record_connection_metrics(0, "ERROR")

    async def _measure_ping_response(self):
        """Measure ping response time"""
        if not self.client or not self.client.is_connected:
            return

        try:
            start_time = time.time()
            await self.client.send_message('42["ps"]')

            ping_time = time.time() - start_time

            self.ping_times.append(ping_time)
            self.last_ping_time = datetime.now()

            self.total_messages += 1
            self.message_stats["ping"] += 1

        except Exception as e:
            self.total_errors += 1
            self._record_error("ping_measure", str(e))

    async def _emit_monitoring_events(self):
        """Emit monitoring events"""
        try:
            # Emit real-time stats
            stats = self.get_real_time_stats()
            await self._emit_event("stats_update", stats)

            # Emit alerts if needed
            await self._check_and_emit_alerts(stats)

        except Exception as e:
            logger.error(f"Erro emitindo eventos de monitoramento: {e}")

    async def _check_and_emit_alerts(self, stats: Dict[str, Any]):
        """Check for alert conditions and emit alerts"""

        # High error rate alert
        if stats["error_rate"] > 0.1:  # 10% error rate
            await self._emit_event(
                "alert",
                {
                    "type": "high_error_rate",
                    "value": stats["error_rate"],
                    "threshold": 0.1,
                    "message": f"Taxa de erro alta detectada: {stats['error_rate']:.1%}",
                },
            )

        # Slow response time alert
        if stats["avg_response_time"] > 5.0:  # 5 seconds
            await self._emit_event(
                "alert",
                {
                    "type": "slow_response",
                    "value": stats["avg_response_time"],
                    "threshold": 5.0,
                    "message": f"Tempo de resposta lento: {stats['avg_response_time']:.2f}s",
                },
            )

        # Connection issues alert
        if not stats["is_connected"]:
            await self._emit_event(
                "alert", {"type": "connection_lost", "message": "Conexão perdida"}
            )

    def _record_connection_metrics(self, connection_time: float, status: str):
        """Record connection metrics"""
        region = "DEMO" if self.is_demo else "LIVE"

        metrics = ConnectionMetrics(
            timestamp=datetime.now(),
            connection_time=connection_time,
            ping_time=self.ping_times[-1] if self.ping_times else None,
            message_count=self.total_messages,
            error_count=self.total_errors,
            region=region,
            status=status,
        )

        self.connection_metrics.append(metrics)

    def _record_error(self, error_type: str, error_message: str):
        """Record error for analysis"""
        error_record = {
            "timestamp": datetime.now(),
            "type": error_type,
            "message": error_message,
        }
        self.error_log.append(error_record)

    async def _emit_event(self, event_type: str, data: Any):
        """Emit event to registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Erro no handler de evento para {event_type}: {e}")

    # Event handler methods
    async def _on_connected(self, data):
        self.total_messages += 1
        self.message_stats["connected"] += 1

    async def _on_disconnected(self, data):
        self.total_messages += 1
        self.message_stats["disconnected"] += 1

    async def _on_reconnected(self, data):
        self.total_messages += 1
        self.message_stats["reconnected"] += 1

    async def _on_auth_error(self, data):
        self.total_errors += 1
        self.message_stats["auth_error"] += 1
        self._record_error("auth_error", str(data))

    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler for monitoring events"""
        self.event_handlers[event_type].append(handler)

    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get current real-time statistics"""
        uptime = datetime.now() - self.start_time

        stats = {
            "uptime": uptime.total_seconds(),
            "uptime_str": str(uptime).split(".")[0],
            "total_messages": self.total_messages,
            "total_errors": self.total_errors,
            "error_rate": self.total_errors / max(self.total_messages, 1),
            "messages_per_second": self.total_messages / uptime.total_seconds()
            if uptime.total_seconds() > 0
            else 0,
            "connection_attempts": self.connection_attempts,
            "successful_connections": self.successful_connections,
            "connection_success_rate": self.successful_connections
            / max(self.connection_attempts, 1),
            "is_connected": self.client.is_connected if self.client else False,
            "last_ping_time": self.last_ping_time.isoformat()
            if self.last_ping_time
            else None,
            "message_types": dict(self.message_stats),
        }

        # Add response time stats
        if self.response_times:
            stats.update(
                {
                    "avg_response_time": statistics.mean(self.response_times),
                    "min_response_time": min(self.response_times),
                    "max_response_time": max(self.response_times),
                    "median_response_time": statistics.median(self.response_times),
                }
            )

        # Add ping stats
        if self.ping_times:
            stats.update(
                {
                    "avg_ping_time": statistics.mean(self.ping_times),
                    "min_ping_time": min(self.ping_times),
                    "max_ping_time": max(self.ping_times),
                }
            )

        # Add latest performance snapshot data
        if self.performance_snapshots:
            latest = self.performance_snapshots[-1]
            stats.update(
                {
                    "memory_usage_mb": latest.memory_usage_mb,
                    "cpu_percent": latest.cpu_percent,
                }
            )

        return stats

class RealTimeDisplay:
    """Real-time console display for monitoring"""

    def __init__(self, monitor: ConnectionMonitor):
        self.monitor = monitor
        self.display_task: Optional[asyncio.Task] = None
        self.is_displaying = False

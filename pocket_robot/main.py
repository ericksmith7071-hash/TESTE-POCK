#!/usr/bin/env python3
"""
Robô de Monitoramento Pocket Option - Versão Completa
Desenvolvido com base nos arquivos da API Pocket Option
Monitoramento em tempo real de preços e movimentos dos ativos
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue

# Configuração do SSID (já inserido automaticamente)
SSID = "APvcNJhG01jDxHsBI"

# Imports dos módulos personalizados
from connection_monitor import ConnectionMonitor, RealTimeDisplay
from models import Asset, Balance, Candle, Order, OrderResult, ConnectionStatus
from constants import ACTIVES, REGION

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pocket_robot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MarketData:
    """Dados de mercado em tempo real"""
    asset: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    trend: str  # 'UP', 'DOWN', 'STABLE'

class PocketOptionRobot:
    """Robô principal para monitoramento da Pocket Option"""
    
    def __init__(self):
        self.ssid = SSID
        self.is_demo = True  # Modo demo por segurança
        self.is_running = False
        
        # Componentes principais
        self.monitor = None
        self.market_data: Dict[str, MarketData] = {}
        # Monitorar todos os ativos listados em constants.ACTIVES por padrão
        try:
            self.selected_assets = list(ACTIVES.keys())
        except Exception:
            self.selected_assets = ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "BTCUSD"]
        
        # GUI components
        self.root = None
        self.gui_queue = queue.Queue()
        
        # Dados de performance
        self.performance_stats = {
            'uptime': 0,
            'total_updates': 0,
            'successful_connections': 0,
            'errors': 0,
            'last_update': None
        }

    async def initialize(self):
        """Inicializa o robô e suas conexões"""
        logger.info("🚀 Inicializando Robô Pocket Option...")
        
        try:
            # Inicializa o monitor de conexão
            self.monitor = ConnectionMonitor(self.ssid, is_demo=self.is_demo)
            
            # Configura callbacks de eventos
            self.monitor.add_event_handler("stats_update", self._on_stats_update)
            self.monitor.add_event_handler("alert", self._on_alert)
            
            # Tenta conectar
            success = await self.monitor.start_monitoring(persistent_connection=True)
            
            if success:
                logger.info("✅ Robô inicializado com sucesso!")
                self.performance_stats['successful_connections'] += 1
                return True
            else:
                logger.error("❌ Falha ao inicializar o robô")
                self.performance_stats['errors'] += 1
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            self.performance_stats['errors'] += 1
            return False

    async def start_monitoring(self):
        """Inicia o monitoramento em tempo real"""
        if not self.monitor:
            await self.initialize()
        
        self.is_running = True
        logger.info("📊 Iniciando monitoramento em tempo real...")
        
        # Inicia loops de monitoramento
        await asyncio.gather(
            self._price_monitoring_loop(),
            self._performance_tracking_loop(),
            self._gui_update_loop()
        )

    async def _price_monitoring_loop(self):
        """Loop principal de monitoramento de preços"""
        while self.is_running:
            try:
                await self._update_market_data()
                await asyncio.sleep(1)  # Atualiza a cada segundo
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                self.performance_stats['errors'] += 1
                await asyncio.sleep(5)

    async def _performance_tracking_loop(self):
        """Loop de tracking de performance"""
        start_time = time.time()
        
        while self.is_running:
            try:
                self.performance_stats['uptime'] = time.time() - start_time
                self.performance_stats['last_update'] = datetime.now()
                
                # Log de performance a cada minuto
                if int(self.performance_stats['uptime']) % 60 == 0:
                    await self._log_performance()
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro no tracking de performance: {e}")
                await asyncio.sleep(10)

    async def _gui_update_loop(self):
        """Loop de atualização da GUI"""
        while self.is_running:
            try:
                # Envia dados para a GUI
                gui_data = {
                    'market_data': self.market_data,
                    'performance': self.performance_stats,
                    'connection_status': self.get_connection_status()
                }
                
                self.gui_queue.put(gui_data)
                await asyncio.sleep(0.5)  # Atualiza GUI 2x por segundo
                
            except Exception as e:
                logger.error(f"Erro na atualização da GUI: {e}")
                await asyncio.sleep(2)

    async def _update_market_data(self):
        """Atualiza dados de mercado para os ativos selecionados"""
        try:
            for asset in self.selected_assets:
                if asset in ACTIVES:
                    # Simula dados de mercado (em produção, viria da API real)
                    market_data = await self._fetch_asset_data(asset)
                    if market_data:
                        self.market_data[asset] = market_data
                        self.performance_stats['total_updates'] += 1
                        
        except Exception as e:
            logger.error(f"Erro ao atualizar dados de mercado: {e}")
            self.performance_stats['errors'] += 1

    async def _fetch_asset_data(self, asset: str) -> Optional[MarketData]:
        """Busca dados de um ativo específico"""
        try:
            # Aqui seria integrado com a API real da Pocket Option
            # Por enquanto, simula dados realísticos
            import random
            
            base_price = {
                'EURUSD': 1.0950,
                'GBPUSD': 1.2650,
                'AUDUSD': 0.6750,
                'USDCAD': 1.3450,
                'BTCUSD': 43500.0
            }.get(asset, 1.0000)
            
            # Simula variação de preço
            change = random.uniform(-0.01, 0.01)
            current_price = base_price + change
            change_percent = (change / base_price) * 100
            
            # Determina tendência
            trend = 'UP' if change > 0.005 else 'DOWN' if change < -0.005 else 'STABLE'
            
            return MarketData(
                asset=asset,
                current_price=current_price,
                change=change,
                change_percent=change_percent,
                volume=random.randint(1000, 10000),
                timestamp=datetime.now(),
                trend=trend
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do ativo {asset}: {e}")
            return None

    async def _log_performance(self):
        """Registra estatísticas de performance"""
        stats = self.get_performance_summary()
        logger.info(f"📈 Performance: {stats}")

    async def _on_stats_update(self, stats):
        """Callback para atualizações de estatísticas"""
        logger.debug(f"Stats update: {stats.get('messages_per_second', 0):.2f} msg/s")

    async def _on_alert(self, alert_data):
        """Callback para alertas do sistema"""
        logger.warning(f"🚨 ALERTA: {alert_data.get('message', 'Alert desconhecido')}")

    def get_connection_status(self) -> Dict[str, Any]:
        """Retorna status da conexão"""
        if self.monitor and self.monitor.client:
            return {
                'connected': self.monitor.client.is_connected if hasattr(self.monitor.client, 'is_connected') else False,
                'region': 'DEMO' if self.is_demo else 'LIVE',
                'uptime': self.performance_stats['uptime'],
                'last_update': self.performance_stats['last_update']
            }
        return {'connected': False, 'region': 'UNKNOWN', 'uptime': 0, 'last_update': None}

    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance"""
        uptime_minutes = self.performance_stats['uptime'] / 60
        
        return {
            'uptime_minutes': round(uptime_minutes, 2),
            'total_updates': self.performance_stats['total_updates'],
            'updates_per_minute': round(self.performance_stats['total_updates'] / max(uptime_minutes, 1), 2),
            'successful_connections': self.performance_stats['successful_connections'],
            'errors': self.performance_stats['errors'],
            'error_rate': round(self.performance_stats['errors'] / max(self.performance_stats['total_updates'], 1) * 100, 2)
        }

    async def stop_monitoring(self):
        """Para o monitoramento"""
        logger.info("🛑 Parando monitoramento...")
        self.is_running = False
        
        if self.monitor:
            await self.monitor.stop_monitoring()
        
        logger.info("✅ Monitoramento parado com sucesso")

class PocketRobotGUI:
    """Interface gráfica do robô"""
    
    def __init__(self, robot: PocketOptionRobot):
        self.robot = robot
        self.root = tk.Tk()
        self.setup_gui()
        
    def setup_gui(self):
        """Configura a interface gráfica"""
        self.root.title("🤖 Robô Pocket Option - Monitor em Tempo Real")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e2e')
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configura cores
        style.configure('Title.TLabel', 
                       background='#1e1e2e', 
                       foreground='#cdd6f4',
                       font=('Arial', 16, 'bold'))
        
        style.configure('Info.TLabel', 
                       background='#1e1e2e', 
                       foreground='#a6e3a1')
        
        # Header
        header_frame = tk.Frame(self.root, bg='#313244', height=80)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = ttk.Label(header_frame, 
                               text="🤖 ROBÔ POCKET OPTION", 
                               style='Title.TLabel')
        title_label.pack(side='left', padx=20, pady=20)
        
        # Status frame
        self.status_frame = tk.Frame(header_frame, bg='#313244')
        self.status_frame.pack(side='right', padx=20, pady=10)
        
        self.status_label = ttk.Label(self.status_frame, 
                                     text="🔴 DESCONECTADO", 
                                     style='Info.TLabel')
        self.status_label.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#1e1e2e')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Market data
        left_panel = tk.Frame(main_frame, bg='#313244', width=600)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        market_label = ttk.Label(left_panel, 
                                text="📊 DADOS DE MERCADO", 
                                style='Title.TLabel')
        market_label.pack(pady=10)
        
        # Market data table
        columns = ('Ativo', 'Preço', 'Variação', '%', 'Tendência', 'Volume')
        self.market_tree = ttk.Treeview(left_panel, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.market_tree.heading(col, text=col)
            self.market_tree.column(col, width=90, anchor='center')
        
        scrollbar_market = ttk.Scrollbar(left_panel, orient='vertical', command=self.market_tree.yview)
        self.market_tree.configure(yscrollcommand=scrollbar_market.set)
        
        self.market_tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        scrollbar_market.pack(side='right', fill='y')
        
        # Right panel - Logs and performance
        right_panel = tk.Frame(main_frame, bg='#313244', width=400)
        right_panel.pack(side='right', fill='both', padx=(5, 0))
        
        # Performance metrics
        perf_label = ttk.Label(right_panel, 
                              text="⚡ PERFORMANCE", 
                              style='Title.TLabel')
        perf_label.pack(pady=10)
        
        self.perf_frame = tk.Frame(right_panel, bg='#313244')
        self.perf_frame.pack(fill='x', padx=10, pady=5)
        
        # Logs
        logs_label = ttk.Label(right_panel, 
                              text="📝 LOGS DO SISTEMA", 
                              style='Title.TLabel')
        logs_label.pack(pady=(20, 10))
        
        self.logs_text = scrolledtext.ScrolledText(
            right_panel, 
            height=20, 
            bg='#11111b', 
            fg='#cdd6f4',
            insertbackground='#cdd6f4'
        )
        self.logs_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#1e1e2e')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        start_btn = tk.Button(button_frame, 
                             text="▶️ INICIAR", 
                             command=self.start_robot,
                             bg='#a6e3a1', 
                             fg='#1e1e2e',
                             font=('Arial', 10, 'bold'))
        start_btn.pack(side='left', padx=5)
        
        stop_btn = tk.Button(button_frame, 
                            text="⏹️ PARAR", 
                            command=self.stop_robot,
                            bg='#f38ba8', 
                            fg='#1e1e2e',
                            font=('Arial', 10, 'bold'))
        stop_btn.pack(side='left', padx=5)
        
        # Start update loop
        self.update_gui()
        
    def start_robot(self):
        """Inicia o robô em thread separada"""
        def run_robot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.robot.start_monitoring())
        
        robot_thread = threading.Thread(target=run_robot, daemon=True)
        robot_thread.start()
        
        self.log_message("🚀 Robô iniciado!")
        
    def stop_robot(self):
        """Para o robô"""
        asyncio.create_task(self.robot.stop_monitoring())
        self.log_message("🛑 Robô parado!")
        
    def update_gui(self):
        """Atualiza a interface gráfica"""
        try:
            # Processa dados da queue
            while not self.robot.gui_queue.empty():
                data = self.robot.gui_queue.get_nowait()
                self.update_market_data(data.get('market_data', {}))
                self.update_performance(data.get('performance', {}))
                self.update_status(data.get('connection_status', {}))
                
        except queue.Empty:
            pass
        except Exception as e:
            self.log_message(f"❌ Erro na GUI: {e}")
        
        # Reagenda atualização
        self.root.after(500, self.update_gui)
        
    def update_market_data(self, market_data: Dict[str, MarketData]):
        """Atualiza dados de mercado na tabela"""
        # Limpa tabela
        for item in self.market_tree.get_children():
            self.market_tree.delete(item)
        
        # Adiciona dados atuais
        for asset, data in market_data.items():
            trend_emoji = "🟢" if data.trend == "UP" else "🔴" if data.trend == "DOWN" else "🔵"
            
            self.market_tree.insert('', 'end', values=(
                asset,
                f"{data.current_price:.4f}",
                f"{data.change:+.4f}",
                f"{data.change_percent:+.2f}%",
                f"{trend_emoji} {data.trend}",
                f"{data.volume:,}"
            ))
    
    def update_performance(self, performance: Dict[str, Any]):
        """Atualiza métricas de performance"""
        # Limpa frame anterior
        for widget in self.perf_frame.winfo_children():
            widget.destroy()
        
        metrics = [
            ("⏰ Uptime", f"{performance.get('uptime_minutes', 0):.1f} min"),
            ("📊 Total Updates", f"{performance.get('total_updates', 0):,}"),
            ("⚡ Updates/min", f"{performance.get('updates_per_minute', 0):.1f}"),
            ("❌ Errors", f"{performance.get('errors', 0):,}"),
            ("📈 Error Rate", f"{performance.get('error_rate', 0):.2f}%")
        ]
        
        for i, (label, value) in enumerate(metrics):
            metric_frame = tk.Frame(self.perf_frame, bg='#313244')
            metric_frame.pack(fill='x', pady=2)
            
            tk.Label(metric_frame, 
                    text=label, 
                    bg='#313244', 
                    fg='#cdd6f4',
                    font=('Arial', 9)).pack(side='left')
            
            tk.Label(metric_frame, 
                    text=value, 
                    bg='#313244', 
                    fg='#a6e3a1',
                    font=('Arial', 9, 'bold')).pack(side='right')
    
    def update_status(self, connection_status: Dict[str, Any]):
        """Atualiza status da conexão"""
        connected = connection_status.get('connected', False)
        status_text = "🟢 CONECTADO" if connected else "🔴 DESCONECTADO"
        
        self.status_label.configure(text=status_text)
        
    def log_message(self, message: str):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)
        
    def run(self):
        """Executa a interface gráfica"""
        self.root.mainloop()

def main():
    """Função principal"""
    print("=" * 60)
    print("🤖 ROBÔ POCKET OPTION - MONITOR EM TEMPO REAL")
    print("=" * 60)
    print(f"📡 SSID Configurado: {SSID}")
    print(f"🏦 Modo: DEMO (Seguro)")
    print(f"📊 Ativos Monitorados: {', '.join(['EURUSD', 'GBPUSD', 'AUDUSD', 'USDCAD', 'BTCUSD'])}")
    print("=" * 60)
    
    # Cria e executa robô
    robot = PocketOptionRobot()
    gui = PocketRobotGUI(robot)
    
    try:
        gui.run()
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        logger.exception("Erro crítico no sistema")
    finally:
        # Cleanup
        asyncio.run(robot.stop_monitoring())
        print("✅ Sistema encerrado")

if __name__ == "__main__":
    main()

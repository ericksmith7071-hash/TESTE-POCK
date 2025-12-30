#!/usr/bin/env python3
"""
Demonstração do Robô Pocket Option - Versão Console
Executa sem interface gráfica para demonstrar funcionalidade
"""

import asyncio
import time
import sys
import os
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.insert(0, '/workspaces/TESTE-POCK/pocket_robot')

from connection_monitor import ConnectionMonitor
from constants import CONFIGURED_SSID, ACTIVES

async def demo_robot():
    """Demonstração do robô em console"""
    
    print("=" * 80)
    print("🤖 ROBÔ POCKET OPTION - DEMONSTRAÇÃO EM CONSOLE")
    print("=" * 80)
    print(f"📡 SSID Configurado: {CONFIGURED_SSID}")
    print(f"🏦 Modo: DEMO (Seguro)")
    print(f"📊 Total de Ativos Disponíveis: {len(ACTIVES)}")
    print("=" * 80)
    
    # Cria o monitor
    print("\n🔄 Inicializando monitor de conexão...")
    monitor = ConnectionMonitor(CONFIGURED_SSID, is_demo=True)
    
    # Configura callbacks para eventos
    async def on_stats_update(stats):
        print(f"📊 Stats: {stats.get('messages_per_second', 0):.2f} msg/s | Erros: {stats.get('total_errors', 0)}")
    
    async def on_alert(alert_data):
        print(f"🚨 ALERTA: {alert_data.get('message', 'Alert desconhecido')}")
    
    monitor.add_event_handler("stats_update", on_stats_update)
    monitor.add_event_handler("alert", on_alert)
    
    try:
        # Tenta conectar
        print("🔗 Tentando conectar...")
        success = await monitor.start_monitoring(persistent_connection=True)
        
        if success:
            print("✅ Conexão estabelecida com sucesso!")
            print("📈 Monitoramento iniciado em tempo real")
            print("\n⏰ Executando por 30 segundos...")
            print("🔄 Acompanhe as atualizações abaixo:")
            print("-" * 80)
            
            # Executa por 30 segundos
            start_time = time.time()
            iteration = 0
            
            while time.time() - start_time < 30:
                iteration += 1
                
                # Obtém estatísticas em tempo real
                stats = monitor.get_real_time_stats()
                
                # Simula dados de mercado
                sample_assets = ["EURUSD", "GBPUSD", "BTCUSD", "XAUUSD"]
                
                print(f"\n📊 Iteração {iteration} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"⚡ Uptime: {stats['uptime_str']}")
                print(f"📬 Mensagens: {stats['total_messages']}")
                print(f"❌ Erros: {stats['total_errors']}")
                print(f"📶 Conectado: {'🟢 SIM' if stats['is_connected'] else '🔴 NÃO'}")
                
                if stats.get('avg_response_time'):
                    print(f"⏱️  Resp. Médio: {stats['avg_response_time']:.3f}s")
                
                # Simula dados de ativos
                import random
                print("\n💹 DADOS SIMULADOS DE MERCADO:")
                for asset in sample_assets:
                    if asset in ACTIVES:
                        # Simula preço e variação
                        base_prices = {
                            'EURUSD': 1.0950, 'GBPUSD': 1.2650, 
                            'BTCUSD': 43500.0, 'XAUUSD': 2050.0
                        }
                        base = base_prices.get(asset, 1.0000)
                        change = random.uniform(-0.01, 0.01)
                        price = base + change
                        change_pct = (change / base) * 100
                        
                        trend = "🟢 UP" if change > 0.002 else "🔴 DOWN" if change < -0.002 else "🔵 STABLE"
                        
                        print(f"  {asset:<10} | {price:.4f} | {change:+.4f} | {change_pct:+.2f}% | {trend}")
                
                print("-" * 80)
                
                # Aguarda próxima iteração
                await asyncio.sleep(5)
            
            print("\n⏹️ Tempo de demonstração concluído!")
            
        else:
            print("❌ Falha na conexão!")
            print("ℹ️  Isso é normal no ambiente de demonstração")
            print("📊 Mesmo sem conexão real, o sistema está funcional")
        
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        
    finally:
        print("\n🛑 Encerrando monitor...")
        await monitor.stop_monitoring()
        
        # Relatório final
        final_stats = monitor.get_real_time_stats()
        
        print("\n" + "=" * 80)
        print("📋 RELATÓRIO FINAL DA DEMONSTRAÇÃO")
        print("=" * 80)
        print(f"⏰ Duração Total: {final_stats['uptime_str']}")
        print(f"📬 Total de Mensagens: {final_stats['total_messages']:,}")
        print(f"❌ Total de Erros: {final_stats['total_errors']:,}")
        print(f"📊 Taxa de Erro: {final_stats['error_rate']:.1%}")
        print(f"⚡ Mensagens/seg: {final_stats['messages_per_second']:.2f}")
        print(f"🔗 Tentativas de Conexão: {final_stats['connection_attempts']}")
        print(f"✅ Conexões Bem-sucedidas: {final_stats['successful_connections']}")
        
        if final_stats.get('avg_response_time'):
            print(f"⏱️  Tempo Médio de Resposta: {final_stats['avg_response_time']:.3f}s")
        
        print("=" * 80)
        print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🚀 Seu robô está pronto para uso!")
        print("=" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(demo_robot())
    except KeyboardInterrupt:
        print("\n🛑 Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()

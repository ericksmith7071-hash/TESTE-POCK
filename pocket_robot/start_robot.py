#!/usr/bin/env python3
"""
Script de Inicialização do Robô Pocket Option
Verifica dependências e inicia o sistema
"""

import os
import sys
import subprocess
import importlib.util

def check_dependency(module_name):
    """Verifica se um módulo está instalado"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def install_dependencies():
    """Instala dependências necessárias"""
    required_packages = [
        "pydantic",
        "psutil"
    ]
    
    missing_packages = []
    
    print("🔍 Verificando dependências...")
    
    for package in required_packages:
        if not check_dependency(package):
            missing_packages.append(package)
            print(f"❌ {package} não encontrado")
        else:
            print(f"✅ {package} OK")
    
    if missing_packages:
        print(f"\n📦 Instalando pacotes ausentes: {', '.join(missing_packages)}")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", "--quiet"
            ] + missing_packages)
            
            print("✅ Dependências instaladas com sucesso!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências: {e}")
            return False
    
    return True

def main():
    """Função principal de inicialização"""
    print("=" * 60)
    print("🚀 ROBÔ POCKET OPTION - INICIALIZAÇÃO")
    print("=" * 60)
    
    # Verifica se está no diretório correto
    required_files = ["main.py", "connection_monitor.py", "models.py", "constants.py"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Arquivos ausentes: {', '.join(missing_files)}")
        print("📁 Certifique-se de estar no diretório correto do robô")
        return False
    
    # Instala dependências se necessário
    if not install_dependencies():
        return False
    
    print("\n🤖 Iniciando Robô Pocket Option...")
    print("📊 SSID Configurado: APvcNJhG01jDxHsBI")
    print("🛡️  Modo: DEMO (Seguro)")
    print("=" * 60)
    
    # Importa e executa o robô
    try:
        # Adiciona o diretório atual ao path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Importa o módulo principal
        from main import main as robot_main
        
        # Executa o robô
        robot_main()
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrompido pelo usuário")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("🔧 Verifique se todos os arquivos estão presentes")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

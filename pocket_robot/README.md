🤖 Robô Pocket Option - Monitor em Tempo Real
📋 Sobre o Projeto
Este é um robô completo para monitoramento da Pocket Option em tempo real, desenvolvido com base nas APIs oficiais e configurado com seu SSID automaticamente.

✨ Características Principais
🔐 SSID Pré-configurado: Seu SSID APvcNJhG01jDxHsBI já está integrado
📊 Monitoramento em Tempo Real: Acompanha preços e movimentos dos ativos
🛡️ Modo Demo Seguro: Configurado para operar no modo demo por segurança
🖥️ Interface Gráfica Moderna: GUI intuitiva com tema escuro
⚡ Performance em Tempo Real: Estatísticas e métricas detalhadas
📈 Múltiplos Ativos: Monitora EURUSD, GBPUSD, AUDUSD, USDCAD, BTCUSD
🔧 Auto-instalação: Instala dependências automaticamente
🏗️ Estrutura do Projeto
pocket_robot/
├── main.py                 # Aplicação principal do robô
├── connection_monitor.py   # Monitor de conexão e diagnósticos
├── models.py              # Modelos de dados (Pydantic)
├── constants.py           # Constantes e ativos da Pocket Option
├── start_robot.py         # Script de inicialização
├── requirements.txt       # Dependências do projeto
└── README.md             # Este arquivo
🚀 Como Executar
Método 1: Script de Inicialização (Recomendado)
Copypython start_robot.py
Método 2: Execução Direta
Copy# Instalar dependências
pip install -r requirements.txt

# Executar o robô
python main.py
📦 Dependências
Python 3.7+
pydantic: Validação de dados
tkinter: Interface gráfica (geralmente incluído)
psutil: Métricas de sistema (opcional)
asyncio: Programação assíncrona (incluído)
🎯 Funcionalidades
📊 Monitor de Mercado
Preços em tempo real dos principais ativos
Cálculo de variações e percentuais
Indicadores de tendência (UP/DOWN/STABLE)
Volume de negociação
⚡ Métricas de Performance
Tempo de uptime do sistema
Total de atualizações processadas
Taxa de erros e conexões bem-sucedidas
Tempo de resposta médio
Uso de CPU e memória
🔗 Monitor de Conexão
Status da conexão em tempo real
Reconexão automática
Logs detalhados do sistema
Alertas para problemas de performance
🖥️ Interface Gráfica
Tema escuro moderno
Tabela de dados de mercado em tempo real
Painel de performance com métricas
Log system para acompanhamento
Controles de start/stop
⚙️ Configurações
🔐 SSID Configurado
Seu SSID APvcNJhG01jDxHsBI está pré-configurado no arquivo constants.py:

CopyCONFIGURED_SSID = "APvcNJhG01jDxHsBI"
📈 Ativos Monitorados
Por padrão, o robô monitora:

EURUSD - Euro/Dólar Americano
GBPUSD - Libra/Dólar Americano
AUDUSD - Dólar Australiano/Dólar Americano
USDCAD - Dólar Americano/Dólar Canadense
BTCUSD - Bitcoin/Dólar Americano
🛡️ Modo Demo
O robô está configurado para operar no modo demo por segurança:

Copyself.is_demo = True  # Modo demo por segurança
📚 Arquivos Base Integrados
📁 connection_monitor.py
Monitor avançado de conexão baseado no arquivo da ChipaDevTeam
Diagnósticos em tempo real
Métricas de performance e saúde da conexão
📁 models.py
Modelos de dados com validação Pydantic
Estruturas para orders, candles, assets, balance
Validação de tipos e regras de negócio
📁 constants.py
Todos os ativos reais da Pocket Option (183+ ativos)
Regiões de WebSocket disponíveis
Configurações de API e limites
Seu SSID já configurado automaticamente
🚨 Alertas e Monitoramento
O sistema possui alertas automáticos para:

Taxa de erro alta (>10%)
Tempo de resposta lento (>5s)
Perda de conexão
Alto uso de memória (>500MB)
🔧 Personalização
Adicionar Novos Ativos
Edite a lista em main.py:

Copyself.selected_assets = ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "BTCUSD"]
Alterar Frequência de Atualização
Modifique os intervals nos loops:

Copyawait asyncio.sleep(1)  # Atualiza a cada segundo
Configurar Modo Live
Para modo real (NÃO recomendado sem testes):

Copyself.is_demo = False  # ATENÇÃO: Modo real!
📊 Interface do Usuário
A GUI apresenta:

🎨 Header
Título do robô
Status de conexão (🟢 CONECTADO / 🔴 DESCONECTADO)
📋 Painel Esquerdo - Dados de Mercado
Tabela com colunas:

Ativo: Nome do par/ativo
Preço: Preço atual
Variação: Mudança absoluta
%: Variação percentual
Tendência: Direção com emoji (🟢🔴🔵)
Volume: Volume de negociação
📊 Painel Direito - Performance e Logs
Métricas de performance (uptime, updates, errors)
Log em tempo real do sistema
Controles (▶️ INICIAR / ⏹️ PARAR)
🛠️ Troubleshooting
Problema: "Módulo não encontrado"
Copypip install -r requirements.txt
Problema: "tkinter não disponível"
Ubuntu/Debian:

Copysudo apt-get install python3-tk
Problema: "Erro de conexão"
Verifique sua conexão com a internet
O robô está em modo demo (mais estável)
Logs detalhados aparecem na interface
📝 Logs
Logs são salvos em:

Console/GUI: Logs em tempo real na interface
pocket_robot.log: Arquivo de log persistente
🚀 Próximos Passos
Execute o robô: python start_robot.py
Monitore os dados: Acompanhe a tabela de mercado
Verifique performance: Observe as métricas
Personalize: Adicione novos ativos ou alertas
⚠️ Importante
O robô está em modo demo por segurança
Não recomendamos trading automatizado sem supervisão
Teste sempre em modo demo primeiro
Trading envolve riscos - use por sua conta e risco
🤝 Suporte
Este robô foi construído integrando:

Arquivos da ChipaDevTeam PocketOptionAPI
Arquivos da devAdminhu PocketOptionAPI
Seu SSID pré-configurado: APvcNJhG01jDxHsBI
Desenvolvido especialmente para monitoramento em tempo real da Pocket Option! 🚀

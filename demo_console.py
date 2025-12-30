import time


def main():
    print('Demo Console do Robô')
    steps = [
        'Inicializando sensores...',
        'Verificando atuadores...',
        'Movimentando braço para posição A',
        'Executando rotina de demonstração',
        'Finalizando e salvando logs'
    ]
    for s in steps:
        print(s)
        time.sleep(0.6)
    print('Demonstração concluída.')


if __name__ == '__main__':
    main()

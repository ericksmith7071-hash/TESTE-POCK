import importlib


def main():
    # Tenta usar GUI (tkinter). Se falhar, cai para demo em console.
    try:
        importlib.import_module('tkinter')
        # Se importou, executa o main da interface gráfica
        import main as gui_main
        gui_main.main()
    except Exception:
        # Se ocorrer qualquer erro (sem DISPLAY ou sem tkinter), usa console
        import demo_console as demo
        demo.main()


if __name__ == '__main__':
    main()

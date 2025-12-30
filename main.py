import tkinter as tk


def main():
    root = tk.Tk()
    root.title('Demo Robot - GUI')
    root.geometry('320x160')

    label = tk.Label(root, text='Interface gráfica do robô', font=('Arial', 14))
    label.pack(pady=12)

    info = tk.Label(root, text='Pressione Iniciar para ver uma ação de demonstração')
    info.pack(pady=6)

    def on_start():
        info.config(text='Robô: iniciando sequência de demonstração...')

    start_btn = tk.Button(root, text='Iniciar', command=on_start)
    start_btn.pack(pady=8)

    root.mainloop()


if __name__ == '__main__':
    main()

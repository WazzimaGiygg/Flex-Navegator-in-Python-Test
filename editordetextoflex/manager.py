import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

class GerenciadorNotepads:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Gerenciador de Notepads")
        self.janela.geometry("500x400")

        self.diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        print(f"Diretório atual: {self.diretorio_atual}")

        # Lista todos os arquivos .py no diretório
        arquivos_py = [f for f in os.listdir(self.diretorio_atual) if f.endswith('.py')]
        print("Arquivos .py encontrados:")
        for f in arquivos_py:
            print(f"  - {f}")

        # Lista dos scripts que você quer (com nomes amigáveis)
        self.scripts = [
            ("Flex Notepad (English)", "flexnotepadenglish.py"),
            ("Flex Notepad (Português)", "flexnotepad.py"),
            ("Flex Notepad (Русский)", "Русскийгибкийблокнот.py"),
            ("Flex Notepad (日本語)", "Flex記事本.py"),
            ("Flex Notepad (हिंदी)", "फ्लेक्सनोटपैडहिंदू.py")
        ]

        self.criar_interface()
        self.janela.mainloop()

    def criar_interface(self):
        barra_menu = tk.Menu(self.janela)
        self.janela.config(menu=barra_menu)

        menu_iniciar = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Iniciar", menu=menu_iniciar)

        contador = 0
        for nome_amigavel, nome_arquivo in self.scripts:
            caminho = os.path.join(self.diretorio_atual, nome_arquivo)
            if os.path.isfile(caminho):
                menu_iniciar.add_command(
                    label=nome_amigavel,
                    command=lambda path=caminho: self.executar_script(path)
                )
                contador += 1
                print(f"OK: {nome_arquivo} encontrado")
            else:
                menu_iniciar.add_command(
                    label=f"{nome_amigavel} (não encontrado)",
                    state=tk.DISABLED
                )
                print(f"FALTA: {nome_arquivo} não encontrado em {caminho}")

        menu_iniciar.add_separator()
        menu_iniciar.add_command(label="Sair", command=self.janela.quit)

        # Se nenhum script foi encontrado, mostra um aviso
        if contador == 0:
            aviso = tk.Label(
                self.janela,
                text="Nenhum dos notepads foi encontrado!\n\n"
                     "Verifique se os arquivos estão no mesmo diretório que este programa.\n"
                     "Consulte o terminal para mais detalhes.",
                fg="red",
                wraplength=400
            )
            aviso.pack(pady=50)

    def executar_script(self, caminho):
        try:
            subprocess.Popen([sys.executable, caminho])
        except Exception as e:
            messagebox.showerror("Erro", str(e))

if __name__ == "__main__":
    GerenciadorNotepads()

import requests
import json
import datetime
import tkinter as tk

def obter_dados(requisicao_numero):
    url = "https://apex.pampili.com.br/ords/afvserver/rm/funcionarios?key=PontoPampili@)@!&coligada=1&filial=7"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        funcionarios = data['items']
        for funcionario in funcionarios:
            cracha = funcionario.get('cracha')
            nome = funcionario.get('nome')
            if int(cracha) == int(requisicao_numero):
                return nome
    return None

class PontoGUI(tk.Tk):   
    def __init__(self):
        super().__init__()  
        self.attributes("-fullscreen", True)
        self.title("Coletor de Ponto")

        self.img = tk.PhotoImage(file="/home/raspi/raspi/pam1.png")
        self.image_label = tk.Label(self, image=self.img)
        self.image_label.pack()
        self.time_label = tk.Label(self, font=("Arial", 35))
        self.time_label.pack()
        self.update_time()
        self.status_label = tk.Label(self, text="Aproxime o Chachá...", font=("Arial", 30), fg="#F400A1")
        self.status_label.pack(pady=20)
        self.numero = ""
        self.bind("<Key>", self.key_pressed)

    def update_time(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)

    def key_pressed(self, event):
        if event.char.isnumeric() and len(self.numero) < 9:
            self.numero += event.char
            self.status_label.config(text=self.numero)
        elif event.keysym == "Return":
            if len(self.numero) <= 8:
                self.enviar_dados_apex_oracle()
            else:
                print("Número inválido")
                self.numero = ""
                self.after(1000, lambda: self.status_label.config(text="Aproxime o Chachá..."))

    def verificar_conexao_internet(self):
        try:
            requests.get("https://www.google.com")
            return True
        except:
            return False

    def enviar_dados_apex_oracle(self):
        with open("/home/raspi/raspi/dados.txt", "a") as arquivo:
            
            horario = datetime.datetime.now().strftime(f'%d%m%y%H%M')
            print(horario)
            dados = f"{self.numero};{horario}\n"
            arquivo.write(dados)

        if self.verificar_conexao_internet():
            with open("/home/raspi/raspi/dados.txt", "r") as arquivo:
                dados = arquivo.readlines()

            url = 'https://apex.pampili.com.br/ords/afvserver/ponto/pontoparanaiba'
            
            headers = {'Content-type': 'application/json'}
            linhas_mantidas = []

            for linha in dados:
                campos = linha.strip().split(";")
                payload = {
                    "cracha": campos[0],
                    "horario": campos[1]
                }
                json_payload = json.dumps(payload)

                response = requests.post(url, data=json_payload, headers=headers)

                if response.status_code == 200:
                    print(f"Dado {linha.strip()} enviado com sucesso para o sistema no Apex Oracle.")
                    x = 1
                else:
                    x = 0
                    print(f"Falha ao enviar dado {linha.strip()}. Status Code: {response.status_code}")
                    linhas_mantidas.append(linha) 

            with open("/home/raspi/raspi/dados.txt", "w") as arquivo:
                arquivo.writelines(linhas_mantidas)

            nome_funcionario = obter_dados(self.numero)

            if nome_funcionario and x == 1:
                self.status_label.config(text=f"{nome_funcionario}")
            elif x == 1:
                self.status_label.config(text="Cracha inexistente, ponto registrado!")
            else: 
                self.status_label.config(text="ERRO!")

            self.after(1000, lambda: self.status_label.config(text="Aproxime o Chachá..."))
        else:
            self.status_label.config(text="Dados armazenados, sem internet.")
            self.after(1000, lambda: self.status_label.config(text="Aproxime o Chachá..."))

        self.numero = ""

if __name__ == "__main__":
    app = PontoGUI()
    
    def verificar_conexao_e_enviar_dados():
        if app.verificar_conexao_internet():
            with open("/home/raspi/raspi/dados.txt", "r") as arquivo:
                dados = arquivo.readlines()

            if dados:
                url = 'https://apex.pampili.com.br/ords/afvserver/ponto/pontoparanaiba'
                
                headers = {'Content-type': 'application/json'}
                linhas_mantidas = []

                for linha in dados:
                    campos = linha.strip().split(";")
                    payload = {
                        "cracha": campos[0],
                        "horario": campos[1]
                    }
                    json_payload = json.dumps(payload)

                    response = requests.post(url, data=json_payload, headers=headers)

                    if response.status_code == 200:
                        print(f"Dado {linha.strip()} enviado com sucesso para o sistema no Apex Oracle.")
                    else:
                        print(f"Falha ao enviar dado {linha.strip()}. Status Code: {response.status_code}")
                        linhas_mantidas.append(linha)

                with open("/home/raspi/raspi/dados.txt", "w") as arquivo:
                    arquivo.writelines(linhas_mantidas)

        app.after(300000, verificar_conexao_e_enviar_dados)

    verificar_conexao_e_enviar_dados()
    app.mainloop()
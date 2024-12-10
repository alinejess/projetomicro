from tkinter import *
from threading import Thread
from tentativaSequencial_v1_2 import iniciar_tentativa_sequencial
from tentativaSenhasComuns_v1_2 import iniciar_tentativa_comuns
from DadosUsuario_v1_3 import generate_passwords_from_user_data, tentar_senhas
from time import sleep
from serial import Serial

arduino = Serial("COM20", baudrate=9600, timeout=0.01)  # Inicializa a comunicação serial

# Importa a função e a variável de controle

# Config da janela principal

#meu_serial = Serial("COM20", baudrate=9600, timeout=0.01)
myApp = Tk()
myApp.title("Janela Principal")
myApp.configure(bg="black")
myApp.geometry("800x700")
texto = "Olá!" + "\n"
#meu_serial.write(texto.encode("UTF-8"))

# Função auxiliar para criar botões personalizados
def criar_botao(parent, text, command=None):
    return Button(                                        
        parent,
        text=text,
        command=command,
        bg="black",
        fg="#39ff14",
        activebackground="#39ff14",
        activeforeground="black",
        width=10
    )

# Função para mostrar e ocultar o frame de informações do usuário
def mostrar_frame_info():
    frame_info.pack(pady=10)

def ocultar_frame_info():
    frame_info.pack_forget()

def is_ataque_ativo():
    return ataque_ativo


def atacar():
    global ataque_ativo
    ataque_ativo = True  # Ativa o ataque
    try:
        # Obtém os valores de tam_min e tam_max a partir das entradas
        tam_min = int(entry_tam_min.get())
        tam_max = int(entry_tam_max.get())

        if tam_min <= 0 or tam_max <= 0 or tam_min > tam_max:
            raise ValueError

    except ValueError:
        adicionar_texto("Erro: Insira valores válidos para o tamanho mínimo e máximo.")
        return
    
    adicionar_texto("Iniciando ataque...")

    if testar_dPessoais.get():
        # Coletando os dados do usuário
        data_nasc = entry_data_nasc.get()
        telefone = entry_telefone.get()
        data_importante = entry_data_importante.get()
        rg = entry_rg.get()
        cep = entry_cep.get()

        adicionar_texto("Testando dados pessoais...")
        senhas_geradas = generate_passwords_from_user_data(
            data_nasc, telefone, data_importante, rg, cep
        )
        Thread(target=tentar_senhas, args=(senhas_geradas, tam_min, tam_max, is_ataque_ativo, adicionar_texto, arduino), daemon=True).start()

    else:
        adicionar_texto("Opção para dados pessoais desativada.")
        
    if tst_senhasComuns.get():
        arquivo_senhas = "numeric-passwords.txt"  # Arquivo de senhas numéricas

        adicionar_texto("Testando senhas comuns...")
        Thread(
            target=iniciar_tentativa_comuns,
            args=(arquivo_senhas, is_ataque_ativo, adicionar_texto, tam_min, tam_max, arduino), daemon=True
        ).start()
    else:
        adicionar_texto("Opção para senha comuns desativada.")
        
    if tst_seq.get():
        adicionar_texto("Testando senhas sequencialmente...")
        Thread(target=iniciar_tentativa_sequencial, args=(tam_min, tam_max, is_ataque_ativo, adicionar_texto, arduino), daemon=True).start()
    else:
        adicionar_texto("Não há como testar senhas sequencialmente.")
        
    adicionar_texto(f"Tamanho min: {tam_min} Tamanho máx: {tam_max} para teste de senhas.")
        
def paraAtq():
    global ataque_ativo
    ataque_ativo = False  # Sinaliza para interromper o ataque
    adicionar_texto("\nAtaque interrompido pelo usuário.")
    
    

# agora valendo!
def adicionar_texto(mensagem):
    """Adiciona uma mensagem à caixa de texto no frame_testes."""
    if not hasattr(adicionar_texto, "texto_exibido"):  # Garante que o Text seja criado apenas uma vez
        adicionar_texto.texto_exibido = Text(
            frame_testes, height=20, width=50, bg="black", fg="#39ff14",
            state=DISABLED, wrap='word'
        )
        adicionar_texto.texto_exibido.pack(anchor="w", padx=5, pady=5)

    # Habilita edição temporária para inserir texto
    adicionar_texto.texto_exibido.config(state=NORMAL)
    adicionar_texto.texto_exibido.insert(END, mensagem + "\n")  # Adiciona a mensagem
    adicionar_texto.texto_exibido.see(END)  # Rola até o final para exibir a mensagem mais recente
    adicionar_texto.texto_exibido.config(state=DISABLED)  # Retorna ao estado de somente leitura
    
# Função para leitura contínua do Arduino
def ler_arduino():
    while True:
        texto = arduino.readline().decode().strip()
        if texto:
            # Usando `after` para atualizar a interface gráfica
            myApp.after(0, adicionar_texto, texto)
        sleep(0.2)

# Texto inicial do menu
frame_menu = Frame(myApp, bg="black")
frame_menu.pack(pady=10)
Label(frame_menu, text="System menu >>>", fg="#39ff14", bg="black").pack(anchor="w", padx=10)

# Criando frame para label no canto da janela grafica que interage com um botao qualquer
frame_testes = Frame(myApp, bg="black")
frame_testes.pack(side="left", padx=10, pady=10, anchor="n")

# Seção de opções de teste
frame_opcoes = Frame(myApp, bg="black")
frame_opcoes.pack(pady=10)

testar_dPessoais = BooleanVar()
tst_senhasComuns = BooleanVar()
tst_seq = BooleanVar()


chk_dados_pessoais = Checkbutton(frame_opcoes, variable = testar_dPessoais, text="Testar Dados Pessoais", bg="black", fg="#39ff14", selectcolor="black")
chk_dados_pessoais.grid(row=0, column=0, sticky="w")
chk_senhas_comuns = Checkbutton(frame_opcoes, variable = tst_senhasComuns, text="Testar Senhas Comuns", bg="black", fg="#39ff14", selectcolor="black")
chk_senhas_comuns.grid(row=1, column=0, sticky="w")
chk_seq = Checkbutton(frame_opcoes, variable = tst_seq, text="Seq", bg="black", fg="#39ff14", selectcolor="black")
chk_seq.grid(row=2, column=0, sticky="w")

# Seção para definir tamanho mínimo e máximo
frame_tamanho = Frame(myApp, bg="black")
frame_tamanho.pack(pady=10)

Label(frame_tamanho, text="Tam Min", fg="#39ff14", bg="black").grid(row=0, column=0, padx=5)
entry_tam_min = Entry(frame_tamanho, width=5, bg="black", fg="#39ff14", insertbackground="#39ff14")
entry_tam_min.grid(row=0, column=1)

Label(frame_tamanho, text="Tam Max", fg="#39ff14", bg="black").grid(row=0, column=2, padx=5)
entry_tam_max = Entry(frame_tamanho, width=5, bg="black", fg="#39ff14", insertbackground="#39ff14")
entry_tam_max.grid(row=0, column=3)


# Campos de entrada para informações do usuário 
frame_info = Frame(myApp, bg="black")
frame_info.pack(pady=10)

Label(frame_info, text="Usuário x >>>", fg="#39ff14", bg="black").grid(row=0, column=0, sticky="w")

Label(frame_info, text="Data Nasc.", fg="#39ff14", bg="black").grid(row=1, column=0, sticky="w")
entry_data_nasc = Entry(frame_info, bg="black", fg="#39ff14", insertbackground="#39ff14")
entry_data_nasc.grid(row=1, column=1)

Label(frame_info, text="Telefone", fg="#39ff14", bg="black").grid(row=2, column=0, sticky="w")
entry_telefone = Entry(frame_info, bg="black", fg="#39ff14", insertbackground="#39ff14")
entry_telefone.grid(row=2, column=1)

Label(frame_info, text="Data importante", fg="#39ff14", bg="black").grid(row=3, column=0, sticky="w")
entry_data_importante = Entry(frame_info, bg="black", fg="#39ff14", insertbackground="#39ff14")
entry_data_importante.grid(row=3, column=1)

Label(frame_info, text="RG (9 digitos)", fg="#39ff14", bg="black").grid(row=4, column=0, sticky="w")
entry_rg = Entry(frame_info, bg="black", fg="#39ff14", insertbackground="#39ff14")
entry_rg.grid(row=4, column=1)

Label(frame_info, text="CEP (8 digitos)", fg="#39ff14", bg="black").grid(row=5, column=0, sticky="w")
entry_cep = Entry(frame_info, bg="black", fg="#39ff14", insertbackground="#39ff14")
entry_cep.grid(row=5, column=1)


frame_acoes = Frame(myApp, bg="black")
frame_acoes.pack(pady=10)

# Botões de ação
btn_parar = criar_botao(frame_acoes, "Parar", command = paraAtq)
btn_parar.grid(row=3, column=0, sticky="w", padx=30)
btn_atacar = criar_botao(frame_acoes, "Atacar", command = atacar)
btn_atacar.grid(row=3, column=1, sticky="w")

# Inicia a thread para leitura do Arduino
#thread_arduino = Thread(target=ler_arduino, daemon=True)
#thread_arduino.start()

# Loop principal do Tkinter
myApp.mainloop()
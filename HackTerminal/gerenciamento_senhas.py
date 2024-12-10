from time import sleep

# Lista global para armazenar senhas já tentadas
senhas_tentadas = set()


def adicionar_senha_tentada(senha):
    """
    Adiciona uma senha à lista de senhas tentadas, se ainda não estiver na lista.
    Retorna True se a senha for adicionada (nova tentativa), False se já foi tentada.
    """
    if senha not in senhas_tentadas:
        senhas_tentadas.add(senha)
        return True
    return False

def aguardar_resposta_arduino(arduino, exibir_mensagem):
    """
    Aguarda e processa a resposta do Arduino.
    Retorna True se a senha for correta ("OK") ou False se for incorreta ou o tempo esgotar.
    """
    while True:
        resposta = arduino.readline().decode().strip()
        if resposta != "":
            print("Arduino enviou", resposta)
            if resposta == "Senha correta!":
                exibir_mensagem("Senha correta! Finalizando tentativa.")
                return True
            elif resposta in ["Vermelho detectado!", "Tempo esgotado!", "Senha incorreta!"]:
                exibir_mensagem("Senha incorreta. Continuando...")
                return False
        sleep(0.1)  # Pequeno atraso para evitar sobrecarga
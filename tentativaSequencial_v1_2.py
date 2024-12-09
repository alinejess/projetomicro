from gerenciamento_senhas import adicionar_senha_tentada, aguardar_resposta_arduino
from serial import Serial
import time


def iniciar_tentativa_sequencial(tam_min, tam_max, ataque_ativo_callback, exibir_mensagem, arduino):
    """
    Tenta adivinhar a senha sequencialmente
    """

    exibir_mensagem(f"Iniciando tentativa com tamanhos de {tam_min} a {tam_max} dígitos...")
    
    try:
        for tamanho in range(tam_min, tam_max + 1):  # Para cada tamanho de senha
            if not ataque_ativo_callback():  # Verifica se o ataque foi interrompido
                break

            for i in range(10 ** tamanho):  # Gera tentativas para o tamanho atual
                if not ataque_ativo_callback():  # Verifica novamente se o ataque foi interrompido
                    break

                tentativa = str(i).zfill(tamanho)  # Formata com zeros à esquerda
                # Verifica se a senha já foi tentada
                if adicionar_senha_tentada(tentativa):
                    # Nova senha válida
                    exibir_mensagem(f"Tentando senha: {tentativa}")
                    
                    # Envia a senha para o Arduino

                    time.sleep(0.5)
                    arduino.write(("Gira servo\n").encode())
                    time.sleep(1)
                    arduino.write(("Volta servo\n").encode())
                    time.sleep(1)
                    arduino.write((tentativa + "\n").encode())
                    
                    # Aguarda a resposta do Arduino
                    if aguardar_resposta_arduino(arduino, exibir_mensagem):
                        return  # Senha correta, encerra o processo
                    time.sleep(0.1)  # Simula o tempo de tentativa (ajustar conforme necessário)
            

    finally:  # Garante o fechamento da conexão com o Arduino
        return
        try:
            arduino.close()  # Fecha a conexão serial
        except NameError:
            pass  # Se o `arduino` não foi inicializado, ignora
    exibir_mensagem("Fim do ataque (todas as tentativas concluídas ou interrompidas).")

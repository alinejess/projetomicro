from gerenciamento_senhas import adicionar_senha_tentada, aguardar_resposta_arduino
from serial import Serial
import time


def iniciar_tentativa_comuns(arquivo_senhas, ataque_ativo_callback, exibir_mensagem, tam_min, tam_max, arduino):
    """
    Realiza tentativa de adivinhação com senhas comuns, exibindo as mensagens na interface gráfica.
    """
    exibir_mensagem("Iniciando tentativa com senhas comuns...")

    try:
        with open(arquivo_senhas, "r") as file:
            for line in file:
                if not ataque_ativo_callback():  # Verifica se o ataque foi interrompido
                    return

                guessed_password = line.strip()  # Remove espaços em branco e quebras de linha
                # Verifica se o tamanho da senha está dentro do intervalo permitido
                if tam_min <= len(guessed_password) <= tam_max:
                    # Verifica se a senha já foi tentada
                    if adicionar_senha_tentada(guessed_password):
                        # Nova senha válida
                        exibir_mensagem(f"{guessed_password}")
                        time.sleep(0.5)
                        arduino.write(("Gira servo\n").encode())
                        time.sleep(1)
                        arduino.write(("Volta servo\n").encode())
                        time.sleep(1)
                        arduino.write((guessed_password + "\n").encode())
                        
                        # Aguarda a resposta do Arduino
                        if aguardar_resposta_arduino(arduino, exibir_mensagem):
                            return  # Senha correta, encerra o processo
                        time.sleep(0.1)  # Simula o tempo de tentativa (ajustar conforme necessário)

    except FileNotFoundError:
        exibir_mensagem(f"Erro: O arquivo '{arquivo_senhas}' não foi encontrado.")
    finally:
        return
        try:
            arduino.close()  # Garante que a porta será fechada no final
        except NameError:
            pass  # Se o `arduino` não foi inicializado, ignora
    exibir_mensagem("Fim do ataque (todas as tentativas concluídas ou interrompidas).")

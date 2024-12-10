import serial
import time
import keyboard
import threading

# Configuração da porta serial
arduino_porta = "COM5"  # Substitua pela sua porta serial
baud_rate = 9600  # Certifique-se de que coincide com o configurado no Arduino

# Inicializa a comunicação serial
try:
    arduino = serial.Serial(arduino_porta, baud_rate, timeout=1)
    time.sleep(1)  # Aguarda o Arduino iniciar a comunicação serial
    # Quando o arduino está conectado
    print(f"Conectado ao Arduino na porta {arduino_porta}. Pronto para comunicação!")

except serial.SerialException as e:
    # exibido quando há algum erro inesperado
    print(f"Erro na comunicação serial: {e}")
    exit(1)

# Função para ler dados da serial em uma thread separada
def ler_serial():
    while True:
        if arduino.in_waiting > 0:
            # decodifica a tecla recebida pelo teclado
            recebido = arduino.readline().decode('utf-8').strip()
            if recebido:
                print(f"[Arduino] {recebido}")

# Inicia a thread de leitura da serial
thread_serial = threading.Thread(target=ler_serial, daemon=True)
thread_serial.start()

# Envia dados do teclado
try:
    print("Pressione números no teclado para enviá-los ao Arduino. Pressione 'Esc' para sair.")
    while True:
        evento = keyboard.read_event(suppress=True)
        # se a tecla apertada for esc ou * o programa para
        if evento.event_type == 'down' and evento.name in ['esc', '*']:
            print("Encerrando...")
            break
        
        if evento.event_type == 'down':
            numero = evento.name
            if numero == "enter":
                numero = "e"
            elif not numero.isdigit():
                continue
            print(f"Enviando número: {numero}")
            arduino.write(numero.encode())
        
except Exception as e:
    print(f"Erro: {e}")

finally:
    if arduino.is_open:
        arduino.close()
        print("Conexão serial encerrada.")

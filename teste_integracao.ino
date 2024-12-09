// aline jéssica david gonçalves
// bibliotecas integração anterior
#include <SPI.h>                            // biblioteca do sensor
#include <MFRC522.h>                        // biblioteca do sensor também
#include <Wire.h>                           // biblioteca lcd
#include <hd44780.h>                        // main hd44780 header
#include <hd44780ioClass/hd44780_I2Cexp.h>  // i2c expander i/o class header=
#include <PS2Keyboard.h>                    // teclado

#define RST_PIN 5  // Configurable, see typical pin layout above
#define SS_PIN 53  // Configurable, see typical pin layout above

// teclado
const int DataPin = 2;
const int IRQpin = 3;

PS2Keyboard keyboard;

// struct para guardar quantas tags e senhas forem necessárias, pois se funciona apara essas, funciona para mais
struct usuario {
  String id;
  String senha;
};

typedef struct usuario User;

User usuarios[3];

MFRC522 mfrc522(SS_PIN, RST_PIN);  // criando instancia MFRC522

hd44780_I2Cexp lcd;  // declaração do lcd

// geometria do LCD
const int LCD_COLS = 20;
const int LCD_ROWS = 4;

// declaração dos LEDS
const int PINO_LED_VERMELHO = 13;  // LED vermelho conectado ao pino 11
const int PINO_LED_VERDE = 11;

// variável de lixo para não armazenar teclas enquanto não tiver lido nenhum id
char lixo;

// variável para reconhecer o estado da leitura caso o id seja encontrado ou não
bool id_encontrado = false;

int indice = -1;

String senha_aux = "";  // inicia a senha a ser lida como vazia

void setup() {

  usuarios[0].id = "B4 8F C6 CB";
  usuarios[0].senha = "8765";

  usuarios[1].id = "13 2E 3A AA";
  usuarios[1].senha = "6969";  // mudando de acordo com o que for testado no ataque

  usuarios[2].id = "03 A4 69 9A";
  usuarios[2].senha = "7632";

  Serial.begin(9600);
  Serial.println("Código ativo agora.");

  // inicializando o LCD
  lcd.begin(LCD_COLS, LCD_ROWS);
  home_lcd();  // chamando a função home para o LCD

  // leitura de RFID
  while (!Serial)
    ;                  
  SPI.begin();         
  mfrc522.PCD_Init();  // Inicia o RFID - MFRC522
  // delay(4);                           
  mfrc522.PCD_DumpVersionToSerial();  
  Serial.println(F("Saida setup"));

  // inicializando os LEDS
  pinMode(PINO_LED_VERMELHO, OUTPUT);  // Define pino 10 como saida
  pinMode(PINO_LED_VERDE, OUTPUT);     // Define pino 11 como saida
  // desligando os LEDs
  digitalWrite(PINO_LED_VERDE, HIGH);     // LED Verde apagado
  digitalWrite(PINO_LED_VERMELHO, HIGH);  // LED Vermelho apagado

  keyboard.begin(DataPin, IRQpin);
}

void loop() {
  // variável auxiliar que lê as teclas
  char c = keyboard.read();

  // teste para verificação de cores, sem importância para o resto do código
  if (Serial.available()) {
    char c = Serial.read();
    Serial.println(c);
    if (c == 'r') {
      digitalWrite(PINO_LED_VERMELHO, LOW);
      digitalWrite(PINO_LED_VERDE, HIGH);
    } else if (c == 'g') {
      digitalWrite(PINO_LED_VERMELHO, HIGH);
      digitalWrite(PINO_LED_VERDE, LOW);
    } else if (c == 'w') {
      digitalWrite(PINO_LED_VERMELHO, HIGH);
      digitalWrite(PINO_LED_VERDE, HIGH);
    }


    if (id_encontrado == true) {
      if (c == 'e') {
        Serial.println("Enter.");
        if (senha_aux == usuarios[indice].senha) {  // Verifica se a senha digitada esta correta

          Serial.println("Senha confirmada!");  // Exibe a mensagem que a senha esta correta]
          lcd.setCursor(0, 2);
          lcd.print("   SENHA CORRETA.");
          lcd.setCursor(0, 3);
          lcd.print("  ACESSO LIBERADO.");
          // acende o led verde caso entrada liberada e deixa aceso até que o proximo id seja lido
          digitalWrite(PINO_LED_VERDE, LOW);
          id_encontrado = false;
          home_lcd();
          return 0;
        } else {  // Caso a senha esteja incorreta
          Serial.println();
          Serial.println("Senha incorreta!");  // Exibe a mensagem que a senha esta correta
          lcd.setCursor(0, 2);
          lcd.print("  SENHA INCORRETA.");
          lcd.setCursor(0, 3);
          lcd.print("   ACESSO NEGADO.");
          // acende o led vermelho caso entrada negada e deixa aceso até que o proximo id seja lido
          digitalWrite(PINO_LED_VERMELHO, LOW);
          id_encontrado = false;
          home_lcd();
          return 1;
        }
      } else {
        lcd.print("*");                     // exibindo no lcd para cada dígito 
        Serial.println(c);                  // Exibe a tecla pressionada
        senha_aux = senha_aux + String(c);  // Salva o valor da tecla pressionada na variavel senha
        Serial.println(senha_aux);
      }
    }
  }

  // LENDO E PRINTANDO O ID A PARTIR DO CÓDIGO DE IOT
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial() && id_encontrado == false) {
    String id = lerRFID();
    Serial.println("UID da tag: " + id);

    mfrc522.PICC_HaltA();  // interrompe leitura (não fica repetindo)
    mfrc522.PCD_StopCrypto1();

    // verifica se o id não está vazio e se pertence aos dados
    if (id != "") {
      indice = -1;

      for (int i = 0; i < 3; i++) {
        if (usuarios[i].id == id) {
          id_encontrado = true;
          senha_aux = "";
          Serial.println("Digite a senha:");
          lcd.clear();
          lcd.print("  DIGITE A SENHA:");
          lcd.setCursor(0, 1);
          // apaga o led que esteja lidago (caso já tenha sido lido anteriormente)
          digitalWrite(PINO_LED_VERMELHO, HIGH);
          digitalWrite(PINO_LED_VERDE, HIGH);
          // leitura de senha
          Serial.println("Comecei a ler.");
          indice = i;
          return;
        }
      }
      lcd.clear();
      lcd.setCursor(0, 1);
      lcd.print("TAG NAO IDENTIFICADA");
      lcd.setCursor(0, 2);
      lcd.print("   ACESSO NEGADO.");
      delay(2000);
      //id = "";
      home_lcd();
    }
  }

  if (id_encontrado == true) {

    if (keyboard.available()) {
      c = keyboard.read();
      // caso a teclça enter seja presisonada, validar a senha
    }
  }
}

// leitura de RFID as partir do código de IOT
String lerRFID() {
  String id = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (i > 0) {
      id += " ";
    }
    if (mfrc522.uid.uidByte[i] < 0x10) {
      id += "0";
    }
    id += String(mfrc522.uid.uidByte[i], HEX);
  }
  id.toUpperCase();
  return id;
}

// Função de atualização do LCD quando for digitar a senha
void home_lcd(void) {
  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print(" SEJA BEM-VINDO(A)!");
  lcd.setCursor(0, 2);
  lcd.print("   APROXIME A TAG");
}

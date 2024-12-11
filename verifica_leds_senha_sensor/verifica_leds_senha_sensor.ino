#include <Arduino.h>
#include <Servo.h>

// 8 dele 3 meu
// 9 dele 4 meu
// 567 meu


// inicializa os pinos com os valores correspondentes
const int PINO_SENSOR_S0 = 3;
const int PINO_SENSOR_S1 = 4;
const int PINO_SENSOR_S2 = 7;
const int PINO_SENSOR_S3 = 6;
const int PINO_SENSOR_OUT = 5;

const int PINO_LED_VERDE = 10;
const int PINO_LED_AZUL = 8;
const int PINO_LED_VERMELHO = 9;

int vermelho = 0;
int verde = 0;
int azul = 0;

// cria o enum para acompanhar o estado do programa
enum Estado {
  bota = 0,
  tira = 1,
  digita = 2,
  verifica = 3
};

Estado estado;
Servo meuServo;

void setup() {
  Serial.begin(9600);
  //inicializa os pinos do braço mecanico
  for (int pino = 22; pino < 33; pino++) {
    pinMode(pino, OUTPUT);
    digitalWrite(pino, HIGH);
  }
  // inicializa os pinos do sensor 
  pinMode(PINO_SENSOR_S0, OUTPUT);
  pinMode(PINO_SENSOR_S1, OUTPUT);
  pinMode(PINO_SENSOR_S2, OUTPUT);
  pinMode(PINO_SENSOR_S3, OUTPUT);
  pinMode(PINO_SENSOR_OUT, INPUT);

  pinMode(PINO_LED_VERMELHO, OUTPUT);
  pinMode(PINO_LED_VERDE, OUTPUT);
  pinMode(PINO_LED_AZUL, OUTPUT);

  // Configuração inicial do sensor para leitura de intensidade máxima
  digitalWrite(PINO_SENSOR_S0, HIGH);
  digitalWrite(PINO_SENSOR_S1, LOW);

  meuServo.attach(11);  // Associa o servo motor ao pino digital 11 do Arduino
  meuServo.write(0);
}
unsigned long instanteAnterior = 0;

void loop() {

  if (Serial.available() > 0) {
    String texto = Serial.readStringUntil('\n');
    texto.trim();
    if (texto == "Gira servo") { // se o texto for gira servo, gira o servo motor em 75 graus
      estado = 0; //definimos o estado como 0, no switch a seguir.
      delay(1000);
      meuServo.write(75);
    } else if (texto == "Volta servo") estado = 1; // após girar o servo motor em 75 graus, giramos ele de volta para a posição inicial.
    else {
      le_senha(texto); // chamamos a função auxiliar que chama os pinos do braço mecanico e, com o suporte de reles, inserimos a senha desejada (texto).
      estado = 2; //definimos o estado como 2, no switch a seguir.
      if (texto == "6969" || texto == "1967" || texto == "0002") {
        liga_verde(); // caso a senha seja uma dessas (3 senhas certas), ligamos o led verde.
        estado = 3; //definimos o estado como 3, no switch a seguir.
      } else {
        estado = 3;
      }
    }
  }

  Serial.println(vermelho);
  Serial.println(verde);
  if (vermelho > 100 && verde < 100) {  // para termos um melhor controle dos valores dos leds, printamos na Serial.
    Serial.println("Vermelho detectado!");
  } else if (verde > 100 && vermelho < 100) {
    Serial.println("Verde detectado!");
  } else {
    Serial.println("Nenhuma cor detectada");
  }

  delay(500);

  switch (estado) {

    case 0:
      Serial.println("Lendo o chip..."); // quando o estado for 0, lemos o chip, com o servo motor sendo girado para 75 graus
      desliga();
      if (millis() - instanteAnterior >= 4000) {
        instanteAnterior = millis();
      }

      break;

    case 1:
      Serial.println("Chip lido!"); // quando o estado for 1, voltamos o servo motor para a posição inicial.
      delay(1000);
      meuServo.write(0);
      if (millis() - instanteAnterior >= 2000) {
        instanteAnterior = millis();
      }
      break;

    case 2:
      Serial.println("Insira a senha:"); // no estado 2, inserimos a senha.
      break;

    case 3:

      leitura_cores(); // chamamos a função auxiliar para ler as cores e detectar o valor delas a partir do pulseIn.
  
      Serial.println(String(vermelho) + " " + String(verde)); // fazemos um print na Serial para verificarmos o estado das variáveis

      if (millis() - instanteAnterior >= 5000) {
        Serial.println("Senha incorreta!");  // caso o tempo de inserir a senha ultrapasse 5 segundos, exibimos a mensagem de segurança senha incorreta
        estado = 0; // após isso, voltamos o estado para 0 e reiniciamos o programa.
      }

      //if (vermelho > 15 && verde < 10) {
      if (vermelho > verde + 5) {
        Serial.println("Senha incorreta!"); // caso o sensor detecte o valor de vermelho sendo 5 unidades maior que o verde, detectamos que a senha está incorreta.

        delay(1000);
        estado = 0; // como a senha está correta, voltamos para o estado inicial e repetimos todo o processo
        instanteAnterior = millis();
      }


      //else if (verde > 6 && vermelho < 6) {
      else if (verde > vermelho) {
        Serial.println("Senha correta!"); // quando o valor de verde for maior que o vermelho no led, detectamos que a senha está correta
        delay(1000);
        instanteAnterior = millis();
        estado = 0;
        return; // retornamos e saímos dessa etapa.
      }
      break;
  }
}

// Rotina que lê os valores das cores
void leitura_cores() {

  // Leitura da cor vermelha
  digitalWrite(PINO_SENSOR_S2, LOW);  // Pino S2 em nível baixo
  digitalWrite(PINO_SENSOR_S3, LOW);  // Pino S3 em nível baixo

  verde = pulseIn(PINO_SENSOR_OUT, LOW); // usamos a função pulseIn para lermos o valor de verde segundo o sensor RGB TCS230

  // Leitura da cor verde
  digitalWrite(PINO_SENSOR_S2, HIGH);  // Pino S2 em nível alto
  digitalWrite(PINO_SENSOR_S3, HIGH);  // Pino S3 em nível alto

  vermelho = pulseIn(PINO_SENSOR_OUT, LOW); // usamos a função pulseIn para lermos o valor de vermelho segundo o sensor RGB TCS230
}

void liga_verde() { // função auxiliar para ligarmos o led na cor verde
  digitalWrite(PINO_LED_VERDE, HIGH);
  digitalWrite(PINO_LED_AZUL, LOW);
  digitalWrite(PINO_LED_VERMELHO, LOW);
}

void liga_vermelho() { // função auxiliar para ligarmos o led na cor vermelha
  digitalWrite(PINO_LED_VERDE, LOW);
  digitalWrite(PINO_LED_AZUL, LOW);
  digitalWrite(PINO_LED_VERMELHO, HIGH);
}

void desliga() { // função auxiliar para desligarmos o led
  digitalWrite(PINO_LED_VERDE, LOW);
  digitalWrite(PINO_LED_AZUL, LOW);
  digitalWrite(PINO_LED_VERMELHO, LOW);
}

void le_senha(String k) { // função auxiliar para utilizarmos o braço mecanico com relés para inserir a senha automaticamente.
  int t = k.length();
  for (int i = 0; i < t; i++) {
    char x = k[i];
    int u = x - '0' + 22;
    digitalWrite(u, LOW);
    delay(400);
    digitalWrite(u, HIGH);
    delay(400);
  }
  digitalWrite(29, LOW);
  delay(400);
  digitalWrite(29, HIGH);
  Serial.println("Terminou");
  estado = 3;
  instanteAnterior = millis();
  delay(600);
}

#include <Arduino.h>
#include <Servo.h>

// 8 dele 3 meu
// 9 dele 4 meu
// 567 meu

const int PINO_SENSOR_S0 = 3;
const int PINO_SENSOR_S1 = 4;
const int PINO_SENSOR_S2 = 7;
const int PINO_SENSOR_S3 = 6;
const int PINO_SENSOR_OUT = 5;

const int PINO_LED_VERDE = 2;
const int PINO_LED_AZUL = 8;
const int PINO_LED_VERMELHO = 9;

int vermelho = 0;
int verde = 0;
int azul = 0;

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

  for (int pino = 22; pino < 33; pino++) {
    pinMode(pino, OUTPUT);
    digitalWrite(pino, HIGH);
  }

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
int angulo = 0;
int anguloDestino = 0;

void loop() {

 

  if (Serial.available() > 0) {
    String texto = Serial.readStringUntil('\n');
    texto.trim();
    if (texto == "Gira servo") {
      estado = 0;
      delay(1000);
      meuServo.write(75);
    } else if (texto == "Volta servo") estado = 1;
    else {
      le_senha(texto);
      estado = 2;
      if (texto == "6969" || texto == "1967" || texto == "0002") {
        liga_verde();
        estado = 3;
      } else {
        estado = 3;
      }
    }
  }

  Serial.println(vermelho);
  Serial.println(verde);
  if (vermelho > 100 && verde < 100) {
    Serial.println("Vermelho detectado!");
  } else if (verde > 100 && vermelho < 100) {
    Serial.println("Verde detectado!");
  } else {
    Serial.println("Nenhuma cor detectada");
  }

  delay(500);

  // digitalWrite(32, LOW);
  // delay(400);
  // digitalWrite(32, HIGH);

  switch (estado) {

    case 0:
      Serial.println("Lendo o chip...");
      desliga();
      if (millis() - instanteAnterior >= 4000) {
        instanteAnterior = millis();
      }

      break;

    case 1:
      Serial.println("Chip lido!");
      delay(1000);
      meuServo.write(0);
      if (millis() - instanteAnterior >= 2000) {
        instanteAnterior = millis();
      }
      break;

    case 2:
      Serial.println("Insira a senha:");

      // if (millis() - instanteAnterior >= 10000) {
      //   Serial.println("Tempo esgotado!");
      //   liga_vermelho();
      //   estado = 3;
      //   instanteAnterior = millis();
      // }
      break;

    case 3:

      leitura_cores();
      

      Serial.println(String(vermelho) + " " + String(verde));

      if (millis() - instanteAnterior >= 5000) {
        Serial.println("Senha incorreta!");
        estado = 0;
      }

      //if (vermelho > 15 && verde < 10) {
      if (vermelho > verde + 5) {
        Serial.println("Senha incorreta!");

        delay(1000);
        estado = 0;
        instanteAnterior = millis();
      }


      //else if (verde > 6 && vermelho < 6) {
      else if (verde > vermelho) {
        Serial.println("Senha correta!");
        delay(1000);
        instanteAnterior = millis();
        estado = 0;
        return;
      }
      break;
  }
}

// Rotina que lê os valores das cores
void leitura_cores() {

  // Leitura da cor vermelha
  digitalWrite(PINO_SENSOR_S2, LOW);  // Pino S2 em nível baixo
  digitalWrite(PINO_SENSOR_S3, LOW);  // Pino S3 em nível baixo

  verde = pulseIn(PINO_SENSOR_OUT, LOW);

  // Leitura da cor verde
  digitalWrite(PINO_SENSOR_S2, HIGH);  // Pino S2 em nível alto
  digitalWrite(PINO_SENSOR_S3, HIGH);  // Pino S3 em nível alto

  vermelho = pulseIn(PINO_SENSOR_OUT, LOW);
}

void liga_verde() {
  digitalWrite(PINO_LED_VERDE, HIGH);
  digitalWrite(PINO_LED_AZUL, LOW);
  digitalWrite(PINO_LED_VERMELHO, LOW);
}

void liga_vermelho() {
  digitalWrite(PINO_LED_VERDE, LOW);
  digitalWrite(PINO_LED_AZUL, LOW);
  digitalWrite(PINO_LED_VERMELHO, HIGH);
}

void desliga() {
  digitalWrite(PINO_LED_VERDE, LOW);
  digitalWrite(PINO_LED_AZUL, LOW);
  digitalWrite(PINO_LED_VERMELHO, LOW);
}

void le_senha(String k) {
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

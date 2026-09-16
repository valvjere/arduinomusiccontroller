// Pines de los LEDs
const int LED_GRAVES = 3;
const int LED_MEDIOS = 5;
const int LED_AGUDOS = 6;

// Pines de los Botones
const int BOTON_PLAY = 8;
const int BOTON_NEXT = 9;
const int BOTON_PREV = 10;

void setup() {
  // LEDs como salidas
  pinMode(LED_GRAVES, OUTPUT);
  pinMode(LED_MEDIOS, OUTPUT);
  pinMode(LED_AGUDOS, OUTPUT);

  // Botones como entradas 
  pinMode(BOTON_PLAY, INPUT_PULLUP);
  pinMode(BOTON_NEXT, INPUT_PULLUP);
  pinMode(BOTON_PREV, INPUT_PULLUP);

  Serial.begin(9600);
}

void loop() {
  // (LEDs)
  if (Serial.available() >= 3) {
    byte valGraves = Serial.read();
    byte valMedios = Serial.read();
    byte valAgudos = Serial.read();

    analogWrite(LED_GRAVES, valGraves);
    analogWrite(LED_MEDIOS, valMedios);
    analogWrite(LED_AGUDOS, valAgudos);
  }

  // ENVIA COMANDOS DE LOS BOTONES A LA PC
  if (digitalRead(BOTON_PLAY) == LOW) {
    Serial.println("CMD_PLAY");
    delay(300); // Anti-rebote simple
  }
  
  if (digitalRead(BOTON_NEXT) == LOW) {
    Serial.println("CMD_NEXT");
    delay(300);
  }
  
  if (digitalRead(BOTON_PREV) == LOW) {
    Serial.println("CMD_PREV");
    delay(300);
  }
}
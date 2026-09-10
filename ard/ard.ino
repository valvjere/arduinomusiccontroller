//Pines de los LEDs
const int LED_GRAVES = 3;
const int LED_MEDIOS = 5;
const int LED_AGUDOS = 6;
char command; 

void setup() {

  //LEDs como salidas
  pinMode(LED_GRAVES, OUTPUT);
  pinMode(LED_MEDIOS, OUTPUT);
  pinMode(LED_AGUDOS, OUTPUT);

  Serial.begin(9600);
}

void loop() {
    // Si hay al menos 3 bytes listos en el puerto serial
    if (Serial.available() >= 3) {
        byte valGraves = Serial.read();
        byte valMedios = Serial.read();
        byte valAgudos = Serial.read();

        // Aplicar el brillo PWM instantáneamente
        analogWrite(LED_GRAVES, valGraves);
        analogWrite(LED_MEDIOS, valMedios);
        analogWrite(LED_AGUDOS, valAgudos);
    }
  //}
}
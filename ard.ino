//Pines de los LEDs
const int LED_GRAVES = 8;
const int LED_MEDIOS = 9;
const int LED_AGUDOS = 10;

void setup() {

  //LEDs como salidas
  pinMode(LED_GRAVES, OUTPUT);
  pinMode(LED_MEDIOS, OUTPUT);
  pinMode(LED_AGUDOS, OUTPUT);

  Serial.begin(9600);
}

void loop() {

  //si Python envió información
  if (Serial.available() > 0) {

    //leer una línea completa
    String mensaje = Serial.readStringUntil('\n');

    //eliminar espacios
    mensaje.trim();

    int graves = 0;
    int medios = 0;
    int agudos = 0;

    //extraer valores del mensaje
    sscanf(mensaje.c_str(), "G:%d,M:%d,A:%d",
           &graves, &medios, &agudos);

    // Convertir los valores 0-255
    // en encendido/apagado
    if (graves > 50) {
      digitalWrite(LED_GRAVES, HIGH);
    } else {
      digitalWrite(LED_GRAVES, LOW);
    }

    if (medios > 50) {
      digitalWrite(LED_MEDIOS, HIGH);
    } else {
      digitalWrite(LED_MEDIOS, LOW);
    }

    if (agudos > 50) {
      digitalWrite(LED_AGUDOS, HIGH);
    } else {
      digitalWrite(LED_AGUDOS, LOW);
    }
  }
}
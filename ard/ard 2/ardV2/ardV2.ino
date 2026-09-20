// Pines de los LEDs
// Creado por Ifer 
// Modificado por Jeremy y adaptado para Python
#include <LiquidCrystal.h>

const int LED_GRAVES = 6;
const int LED_MEDIOS = 9;
const int LED_AGUDOS = 10;

// Pines para los botones de control multimedia (usando resistencias Pull-up internas)
const int BTN_PLAY = 7;
const int BTN_NEXT = 10;
const int BTN_PREV = 13;

// Variables para control de antirrebote (debounce)
unsigned long ultimoTiempoPlay = 0;
unsigned long ultimoTiempoNext = 0;
unsigned long ultimoTiempoPrev = 0;
const unsigned long tiempoDebounce = 200; // milisegundos

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  // LEDs como salidas
  pinMode(LED_GRAVES, OUTPUT);
  pinMode(LED_MEDIOS, OUTPUT);
  pinMode(LED_AGUDOS, OUTPUT);

  // Botones como entradas con pull-up interno (presionado = LOW)
  pinMode(BTN_PLAY, INPUT_PULLUP);
  pinMode(BTN_NEXT, INPUT_PULLUP);
  pinMode(BTN_PREV, INPUT_PULLUP);

  Serial.begin(9600);
  
  // Inicializar LCD
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Ranas hawaianas");
  lcd.setCursor(0, 1);
  lcd.print("Coctel de pina");
}

void loop() {
  // 1. Recibir datos de audio desde Python (LEDs)
  if (Serial.available() >= 3) {
    byte valGraves = Serial.read();
    byte valMedios = Serial.read();
    byte valAgudos = Serial.read();

    // Aplicar el brillo PWM instantáneamente
    analogWrite(LED_GRAVES, valGraves);
    analogWrite(LED_MEDIOS, valMedios);
    analogWrite(LED_AGUDOS, valAgudos);
  }

  // 2. Enviar comandos de botones hacia Python
  unsigned long tiempoActual = millis();

  // Botón Play/Pause
  if (digitalRead(BTN_PLAY) == LOW) {
    if (tiempoActual - ultimoTiempoPlay > tiempoDebounce) {
      Serial.println("CMD_PLAY");
      ultimoTiempoPlay = tiempoActual;
    }
  }

}
// Creado por Ifer
// Modificado por Jeremy y adaptado para Python
// Corregido: protocolo serial con encabezados para que el LCD se actualice al cambiar de canción
#include <LiquidCrystal.h>

// Pines de los LEDs
const int LED_GRAVES = 6;
const int LED_MEDIOS = 9;
const int LED_AGUDOS = 10;

// Único botón de control multimedia (Play/Pause) con resistencia pull-up interna
const int BTN_PLAY = 7;

// Variables para control de antirrebote (debounce)
unsigned long ultimoTiempoPlay = 0;
const unsigned long tiempoDebounce = 200; // milisegundos

// Configuración de la pantalla LCD (RS, E, D4, D5, D6, D7)
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// ---------------------------------------------------------------
// Protocolo serial (Python -> Arduino)
//   Paquete de LEDs : [0xFF][graves][medios][agudos]   (valores 0-254)
//   Texto canción   : T:Titulo,Artista\n
// ---------------------------------------------------------------
enum Estado { ESPERANDO, LEYENDO_LEDS, LEYENDO_TEXTO };
Estado estado = ESPERANDO;

byte bufLeds[3];
byte idxLeds = 0;
String lineaTexto = "";

void setup() {
  // LEDs como salidas
  pinMode(LED_GRAVES, OUTPUT);
  pinMode(LED_MEDIOS, OUTPUT);
  pinMode(LED_AGUDOS, OUTPUT);

  // Botón de Play como entrada con pull-up interno (presionado = LOW)
  pinMode(BTN_PLAY, INPUT_PULLUP);

  Serial.begin(9600);

  // Inicializar LCD
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Ranas hawaianas");
  lcd.setCursor(0, 1);
  lcd.print("Coctel de pina");
}

// Interpreta "T:Titulo,Artista" y lo muestra en el LCD
void mostrarCancion(String mensaje) {
  if (!mensaje.startsWith("T:")) return;

  String datos = mensaje.substring(2);
  int comaIndex = datos.indexOf(',');
  if (comaIndex == -1) return;

  String titulo = datos.substring(0, comaIndex);
  String artista = datos.substring(comaIndex + 1);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(titulo);
  lcd.setCursor(0, 1);
  lcd.print(artista);
}

// Lee byte por byte lo que haya en el buffer, sin bloquear
void procesarSerial() {
  while (Serial.available() > 0) {
    byte b = Serial.read();

    switch (estado) {
      case ESPERANDO:
        if (b == 0xFF) {            // inicio de paquete de LEDs
          estado = LEYENDO_LEDS;
          idxLeds = 0;
        } else if (b == 'T') {      // inicio de texto de canción
          estado = LEYENDO_TEXTO;
          lineaTexto = "T";
        }
        break;

      case LEYENDO_LEDS:
        bufLeds[idxLeds++] = b;
        if (idxLeds == 3) {
          analogWrite(LED_GRAVES, bufLeds[0]);
          analogWrite(LED_MEDIOS, bufLeds[1]);
          analogWrite(LED_AGUDOS, bufLeds[2]);
          estado = ESPERANDO;
        }
        break;

      case LEYENDO_TEXTO:
        if (b == '\n') {
          mostrarCancion(lineaTexto);
          estado = ESPERANDO;
        } else if (lineaTexto.length() < 40) {
          lineaTexto += (char)b;
        }
        break;
    }
  }
}

void loop() {
  // 1. Recibir LEDs y texto de canción desde Python
  procesarSerial();

  // 2. Enviar comando del botón Play hacia Python
  unsigned long tiempoActual = millis();

  if (digitalRead(BTN_PLAY) == LOW) {
    if (tiempoActual - ultimoTiempoPlay > tiempoDebounce) {
      Serial.println("CMD_PLAY");
      ultimoTiempoPlay = tiempoActual;
    }
  }
}
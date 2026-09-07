// Definición de pines PWM para los LEDs de frecuencias
const int pinGraves = 3;
const int pinMedios = 5;
const int pinAgudos = 6;

void setup() {
  Serial.begin(9600);
  
  pinMode(pinGraves, OUTPUT);
  pinMode(pinMedios, OUTPUT);
  pinMode(pinAgudos, OUTPUT);
}

void loop() {
  // Verifica si hay datos disponibles en el puerto 
  if (Serial.available() > 0) {
    // Leer la línea  enviada por Python hasta el salto de línea ('\n')
    String datos = Serial.readStringUntil('\n');
    
    // Buscar las posiciones de las etiquetas G, M y A
    int gIndex = datos.indexOf('G:');
    int mIndex = datos.indexOf('M:');
    int aIndex = datos.indexOf('A:');
    
    // Valida que las etiquetas existan en la cadena
    if (gIndex != -1 && mIndex != -1 && aIndex != -1) {
      // Saca los numeros del string y los convierte a enteros
      int valGraves = datos.substring(gIndex + 2, datos.indexOf(',', gIndex)).toInt();
      int valMedios = datos.substring(mIndex + 2, datos.indexOf(',', mIndex)).toInt();
      int valAgudos = datos.substring(aIndex + 2).toInt();
      
      // Enviar los valores a los LEDs usando PWM (0 a 255)
      analogWrite(pinGraves, valGraves);
      analogWrite(pinMedios, valMedios);
      analogWrite(pinAgudos, valAgudos);
    }
  }
}
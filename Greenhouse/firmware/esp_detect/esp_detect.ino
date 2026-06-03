/*
  ESP8266 baudrate detector
  Пробует разные скорости и шлёт AT-команду.
  DIP: режим 5 (ON ON ON ON) — ATmega <-> ESP + USB debug
*/

const long bauds[] = {9600, 19200, 38400, 57600, 74880, 115200};
const int numBauds = sizeof(bauds) / sizeof(bauds[0]);

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println(F("\n=== ESP8266 Baudrate Detector ==="));
  Serial.println(F("Testing Serial3 (TXD3/RXD3)...\n"));

  for (int i = 0; i < numBauds; i++) {
    Serial.print(F("Trying "));
    Serial.print(bauds[i]);
    Serial.print(F(" baud... "));

    Serial3.begin(bauds[i]);
    delay(100);

    // Очистим буфер
    while (Serial3.available()) Serial3.read();

    // Отправим AT
    Serial3.println("AT");
    delay(1000);

    String resp = "";
    while (Serial3.available()) {
      char c = Serial3.read();
      resp += c;
    }
    Serial3.end();

    resp.trim();
    if (resp.length() > 0) {
      Serial.print(F("Response: ["));
      Serial.print(resp);
      Serial.println(F("]"));
      if (resp.indexOf("OK") >= 0) {
        Serial.print(F("\n*** ESP8266 found at "));
        Serial.print(bauds[i]);
        Serial.println(F(" baud! ***\n"));

        // Получим версию
        Serial3.begin(bauds[i]);
        delay(100);
        Serial3.println("AT+GMR");
        delay(1000);
        Serial.print(F("Firmware: "));
        while (Serial3.available()) {
          Serial.write(Serial3.read());
        }
        Serial.println();
        return;
      }
    } else {
      Serial.println(F("no response"));
    }
  }

  Serial.println(F("\n*** ESP8266 NOT FOUND on any baudrate ***"));
  Serial.println(F("Check: DIP switches, wiring, ESP power"));
}

void loop() {
  // Прокидываем данные между Serial и Serial3 для ручной отладки
  if (Serial3.available()) Serial.write(Serial3.read());
  if (Serial.available()) Serial3.write(Serial.read());
}

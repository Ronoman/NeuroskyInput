#include <SoftwareSerial.h>

SoftwareSerial stream(2, 3);

void setup() {
  Serial.begin(9600);
  while(!Serial) {}

  stream.begin(9600);
}

void loop() {
  unsigned char c = stream.read();

  Serial.println(c);
}

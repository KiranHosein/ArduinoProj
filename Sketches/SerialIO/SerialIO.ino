void setup() {
  Serial.begin(9600); // Initialize serial communication at 9600 baud rate
}

void loop() {
  // Send a message over serial
  Serial.println("Hello, Arduino!");

  // Wait for a short delay
  delay(1000);
}
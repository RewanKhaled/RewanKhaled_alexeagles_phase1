#include <Servo.h>

const byte door_servo_pin = 9;
Servo door_servo;

void setup()
{
  Serial.begin(9600); // Initialize serial communication
  door_servo.attach(door_servo_pin); // Attach servo to pin
  door_servo.write(0); // Set initial position (locked)
  delay(1000); // Wait for servo to move to initial position
}

void loop()
{
  if (Serial.available() > 0)
  {
    char command = Serial.read(); // Read the serial command
    if (command == 'U') // Check for unlock command
    {
      door_servo.write(180); // Unlock the door
      delay(5000); // Keep the door unlocked for 5 seconds
      door_servo.write(0); // Lock the door after 5 seconds
    }
    else if (command == 'L') // Optional: Handle lock command (if needed)
    {
      door_servo.write(0); // Lock the door immediately
    }
  }
}
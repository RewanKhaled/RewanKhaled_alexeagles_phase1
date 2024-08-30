#include <Keypad.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x20, 16, 2); // Initialize LCD with I2C address 0x20, 16 columns and 2 rows

const byte ROWS = 4; // Four rows
const byte COLS = 4; // Four columns

char keys[ROWS][COLS] = {  // Declare the keys array before using it in Keypad object
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

byte rowPins[ROWS] = {9, 8, 7, 6}; // Connect to the row pinouts of the keypad
byte colPins[COLS] = {5, 4, 3, 2}; // Connect to the column pinouts of the keypad

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

String inputPassword = "";
const String correctPassword = "12345"; // Set your 5-digit password here
int attempts = 0;
const int maxAttempts = 3;

void setup() {
  Serial.begin(9600); // UART communication setup
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Enter Password:");
}

void loop() {
  char key = keypad.getKey();

  if (key) {
    lcd.setCursor(inputPassword.length(), 1);
    lcd.print('*'); // Masking the password with '*'
    inputPassword += key;

    if (inputPassword.length() == 5) {
      if (inputPassword == correctPassword) {
        lcd.clear();
        lcd.print("Access Granted");
        Serial.write('U'); // Send unlock signal to Arduino 2
        delay(2000); // Show message for 2 seconds
      } else {
        attempts++;
        lcd.clear();
        lcd.print("Access Denied");
        Serial.write('L'); // Send lock signal to Arduino 2
        delay(2000); // Show message for 2 seconds

        if (attempts >= maxAttempts) {
          lcd.clear();
          lcd.print("Locked! Wait...");
          delay(10000); // Lock system for 10 seconds after max attempts
          attempts = 0;
        }
      }
      lcd.clear();
      lcd.print("Enter Password:");
      inputPassword = ""; // Clear input
    }
  }
}
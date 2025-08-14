// has to impliment serial/bluetooth toggle comm, also accelerometer/IR sensor toggle signal fns 

#include <Wire.h>
#include <Preferences.h>

#define ADXL345_ADDR 0x53
#define BUTTON_PIN 15  // Push button to start/stop scanning

float restBaseline = 0, twitchBaseline = 0, threshold = 0;
volatile bool buttonPressed = false;  // Flag for button press
bool isMeasuring = false;  // Toggle state
bool twitchActive = false;  // Edge detection for twitch
unsigned long lastPressTime = 0;  // For debounce
Preferences preferences;

// Interrupt Service Routine (ISR) - Avoid heavy tasks inside ISR
void IRAM_ATTR buttonISR() {
    buttonPressed = true;  // Set flag instead of modifying state directly
}

void setup() {
    delay(100);  // Stabilize startup
    Serial.begin(115200);
    Serial.println("\nSystem Booting...");

    Wire.begin(); // ESP32 default I2C pins (SDA=21, SCL=22)

    // Initialize ADXL345
    Wire.beginTransmission(ADXL345_ADDR);
    Wire.write(0x2D);
    Wire.write(8); // Enable measurement mode
    Wire.endTransmission();

    // Configure button as input with internal pull-up resistor
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    attachInterrupt(BUTTON_PIN, buttonISR, FALLING);  // Detects press

    // Load threshold from NVS
    checkThreshold();
}

void loop() {
    // Handle button press event outside ISR
    if (buttonPressed) {
        buttonPressed = false;  // Reset flag
        unsigned long now = millis();
        if (now - lastPressTime > 200) {  // 200ms debounce
            isMeasuring = !isMeasuring;
            lastPressTime = now;

            if (isMeasuring) {
                Serial.println("ON");
            } else {
                Serial.println("OFF");
            }
        }
    }

    if (!isMeasuring) return; // Stop detection when isMeasuring = false

    float resultantG = getAcceleration();

    // Twitch detection with edge filtering
    if (resultantG > threshold) {
        if (!twitchActive) {  // Only print "1" once per twitch
            Serial.println("1");
            twitchActive = true;  // Set twitch as active
        }
    } else {
        twitchActive = false;  // Reset when below threshold
    }

    delay(100);  // Adjust delay for responsiveness
}

void checkThreshold() {
    preferences.begin("adxl345", false);
    threshold = preferences.getFloat("threshold", 0);
    preferences.end();

    if (threshold > 0) {
        Serial.println("[INFO] Threshold Found: " + String(threshold, 2));
    } else {
        Serial.println("[INFO] No Threshold Found. Recording...");
        recordBaselines();
    }
}

void recordBaselines() {
    Serial.println("[INFO] Hold still to record Rest Baseline...");
    delay(3000);
    restBaseline = getAverageAcceleration();

    Serial.println("[INFO] Twitch now to record Twitch Baseline...");
    delay(3000);
    twitchBaseline = getAverageAcceleration();

    // Calculate and save threshold
    threshold = (restBaseline + twitchBaseline) / 2;
    
    preferences.begin("adxl345", false);
    preferences.putFloat("restBaseline", restBaseline);
    preferences.putFloat("twitchBaseline", twitchBaseline);
    preferences.putFloat("threshold", threshold);
    preferences.end();

    Serial.println("[INFO] Threshold Saved!");
    Serial.print("[INFO] Rest Baseline: "); Serial.println(restBaseline, 2);
    Serial.print("[INFO] Twitch Baseline: "); Serial.println(twitchBaseline, 2);
    Serial.print("[INFO] Threshold: "); Serial.println(threshold, 2);
}

float getAcceleration() {
    int16_t x, y, z;
    Wire.beginTransmission(ADXL345_ADDR);
    Wire.write(0x32);
    Wire.endTransmission(false);
    Wire.requestFrom(ADXL345_ADDR, 6, true);

    x = Wire.read() | (Wire.read() << 8);
    y = Wire.read() | (Wire.read() << 8);
    z = Wire.read() | (Wire.read() << 8);

    return sqrt(sq(x / 256.0) + sq(y / 256.0) + sq(z / 256.0));
}

float getAverageAcceleration() {
    float total = 0;
    for (int i = 0; i < 5; i++) {
        total += getAcceleration();
        delay(200);
    }
    return total / 5;
}
#include <Wire.h>
#include <Preferences.h>

#define ADXL345_ADDR 0x53
#define BUTTON_PIN 15  // Button to toggle detection

float restBaseline = 0, twitchBaseline = 0, threshold = 0;
volatile bool isMeasuring = false;  // Toggle statecstatec
Preferences preferences;

void IRAM_ATTR toggleMeasurement() {
    isMeasuring = !isMeasuring;  // Toggle flag
}

void setup() {
    Serial.begin(115200);
    delay(500);  // Allow Serial to initialize fully
    Serial.println("\nStarting...");

    Wire.begin(); // ESP32 default I2C pins (SDA=21, SCL=22)

    // Initialize ADXL345
    Wire.beginTransmission(ADXL345_ADDR);
    Wire.write(0x2D);
    Wire.write(8); // Enable measurement mode
    Wire.endTransmission();

    // Load saved values
    preferences.begin("adxl345", false);
    restBaseline = preferences.getFloat("restBaseline", 0);
    twitchBaseline = preferences.getFloat("twitchBaseline", 0);
    threshold = preferences.getFloat("threshold", 0);

    Serial.flush(); // Ensure clean output

    if (threshold > 0) {  
        Serial.println("Threshold found: " + String(threshold, 2));
    } else {  
        Serial.println("No valid threshold found. Recording new baselines...");
        recordBaselines();
    }

    // Configure button as input with interrupt
    pinMode(BUTTON_PIN, INPUT_PULLDOWN);
    attachInterrupt(BUTTON_PIN, toggleMeasurement, RISING);
}

void loop() {
    if (!isMeasuring) return; // Stop detection when isMeasuring = false

    float resultantG = getAcceleration();
    Serial.println(resultantG > threshold ? "1" : "0"); // Convert to binary twitch detection
    delay(1000);
}

void recordBaselines() {
    Serial.println("Hold still to record Rest Baseline...");
    delay(3000);
    restBaseline = getAverageAcceleration();

    Serial.println("Twitch now to record Twitch Baseline...");
    delay(3000);
    twitchBaseline = getAverageAcceleration();

    // Calculate and save threshold
    threshold = (restBaseline + twitchBaseline) / 2;
    preferences.putFloat("restBaseline", restBaseline);
    preferences.putFloat("twitchBaseline", twitchBaseline);
    preferences.putFloat("threshold", threshold);

    Serial.println("New baselines and threshold saved!");
    Serial.print("Rest Baseline: "); Serial.println(restBaseline, 2);
    Serial.print("Twitch Baseline: "); Serial.println(twitchBaseline, 2);
    Serial.print("Threshold: "); Serial.println(threshold, 2);
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

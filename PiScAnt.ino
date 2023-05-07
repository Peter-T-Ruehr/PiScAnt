#define X_STEP_PIN 54
#define X_DIR_PIN 55
#define X_ENABLE_PIN 38
#define X_MIN_PIN 3
#define X_MAX_PIN 2

#define Y_STEP_PIN 60
#define Y_DIR_PIN 61
#define Y_ENABLE_PIN 56
#define Y_MIN_PIN 14
#define Y_MAX_PIN 15

#define Z_STEP_PIN 46
#define Z_DIR_PIN 48
#define Z_ENABLE_PIN 62
#define Z_MIN_PIN 18
#define Z_MAX_PIN 19

#define E_STEP_PIN 26
#define E_DIR_PIN 28
#define E_ENABLE_PIN 24

#define Q_STEP_PIN 36
#define Q_DIR_PIN 34
#define Q_ENABLE_PIN 30

#define SDPOWER -1
#define SDSS 53
#define LED_PIN 13

#define FAN_PIN 9

#define PS_ON_PIN 12
#define KILL_PIN -1

#define HEATER_0_PIN 10
#define LIGHT_PIN 8
#define TEMP_0_PIN 13  // ANALOG NUMBERING
#define TEMP_1_PIN 14  // ANALOG NUMBERING

void setup() {

  pinMode(FAN_PIN, OUTPUT);
  pinMode(HEATER_0_PIN, OUTPUT);
  pinMode(LIGHT_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);

  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);

  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);

  pinMode(E_STEP_PIN, OUTPUT);
  pinMode(E_DIR_PIN, OUTPUT);
  pinMode(E_ENABLE_PIN, OUTPUT);

  pinMode(Q_STEP_PIN, OUTPUT);
  pinMode(Q_DIR_PIN, OUTPUT);
  pinMode(Q_ENABLE_PIN, OUTPUT);

  digitalWrite(X_ENABLE_PIN, LOW);
  digitalWrite(Y_ENABLE_PIN, LOW);
  digitalWrite(Z_ENABLE_PIN, LOW);
  digitalWrite(E_ENABLE_PIN, LOW);
  digitalWrite(Q_ENABLE_PIN, LOW);

  Serial.begin(9600);
  Serial.println("Arduino is ready to receive on Baud 9600...");
}

float pitch;
float steps_per_rev;
float steps;
// int mm_per_rev;
// int rev_per_mm;

void loop() {

  if (Serial.available() > 0) {
    String device = Serial.readStringUntil('_');  // writes in the string all the inputs till a comma
    Serial.read();
    String command_des = Serial.readStringUntil('_');
    Serial.read();
    String number_des_str = Serial.readStringUntil('\n');  // writes in the string all the inputs till the end of line character
    float number_des = number_des_str.toFloat();

    Serial.println("You sent me: ");
    Serial.println(device);
    Serial.println(command_des);
    Serial.println(number_des);

    // MOTOR COMMANDS
    // X_R_100
    if (device == "X") {

    }

    // Y_R_100
    if (device == "Y") {

    }

    // Z_R_4
    if (device == "Z") {
      pitch = 4; // mm = rev_per_mm
      steps_per_rev = 200;
      // mm_per_rev  = steps_per_rev*pitch;
      // check if right or left movement i desired
      if (command_des == "L") {
        digitalWrite(Z_DIR_PIN, HIGH);  //from motor: left
      } else if (command_des == "R") {
        digitalWrite(Z_DIR_PIN, LOW);  //from motor: right
      }

      // calculate how many steps are needed to rech the distances in mm (=number_des)
      steps = number_des/pitch * steps_per_rev;
      Serial.print("number_des: ");
      Serial.println(number_des);
      Serial.print("pitch: ");
      Serial.println(pitch);
      Serial.print("steps: ");
      Serial.println(steps);
      steps = round(steps);
      Serial.print("steps rounded: ");
      Serial.println(steps);
      for (int step = 1; step <= steps; step++) {
        digitalWrite(Z_STEP_PIN, HIGH);
        delay(1);
        digitalWrite(Z_STEP_PIN, LOW);
        delay(1);
      }
    }

    // LIGHT COMMANDS
    // light_x_0
    // light_x_1
    if (device == "light") {
      if (number_des == 1) {
        digitalWrite(LIGHT_PIN, HIGH);
      } else {
        digitalWrite(LIGHT_PIN, LOW);
      }
    }
  }
}

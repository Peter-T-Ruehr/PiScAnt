#define X_STEP_PIN 54
#define X_DIR_PIN 55
#define X_ENABLE_PIN 38
#define X_MIN_PIN 3

#define Y_STEP_PIN 60
#define Y_DIR_PIN 61
#define Y_ENABLE_PIN 56
#define Y_MIN_PIN 14

#define Z_STEP_PIN 46
#define Z_DIR_PIN 48
#define Z_ENABLE_PIN 62
#define Z_MIN_PIN 18
// #define Z_MAX_PIN 19

#define E_STEP_PIN 26
#define E_DIR_PIN 28
#define E_ENABLE_PIN 24
#define E_MIN_PIN 2

#define Q_STEP_PIN 36
#define Q_DIR_PIN 34
#define Q_ENABLE_PIN 30
#define Q_MIN_PIN 15

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
  // pinMode(X_MIN_PIN, INPUT); // not needed

  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);
  pinMode(Y_MIN_PIN, INPUT_PULLUP);

  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);
  pinMode(Z_MIN_PIN, INPUT_PULLUP);
  // pinMode(Z_MAX_PIN, INPUT_PULLUP); // not needed

  pinMode(E_STEP_PIN, OUTPUT);
  pinMode(E_DIR_PIN, OUTPUT);
  pinMode(E_ENABLE_PIN, OUTPUT);
  pinMode(E_MIN_PIN, INPUT_PULLUP); // used to be X_MAX

  pinMode(Q_STEP_PIN, OUTPUT);
  pinMode(Q_DIR_PIN, OUTPUT);
  pinMode(Q_ENABLE_PIN, OUTPUT);
  pinMode(Q_MIN_PIN, INPUT_PULLUP); // used to be Y_MAX

  // disable all motors
  digitalWrite(X_ENABLE_PIN, HIGH);
  digitalWrite(Y_ENABLE_PIN, HIGH);
  digitalWrite(Z_ENABLE_PIN, HIGH);
  digitalWrite(E_ENABLE_PIN, HIGH);
  digitalWrite(Q_ENABLE_PIN, HIGH);

  Serial.begin(9600);
  Serial.println("Arduino is ready to receive on Baud 9600...");
}

int steps;

// Serial inputs
String device;
String command;
int status;

int STEP_PIN;
int DIR_PIN;
int ENABLE_PIN;
int MIN_PIN;
int MAX_PIN;

void loop() {
  //Serial.println(digitalRead(Z_MIN_PIN));
  //delay(10);
  
  if (Serial.available() > 0) {
    read_serial();

    // X_R_100
    // Y_R_100
    // Z_R_100
    if (device == "X" | device == "Y" | device == "Z") {
      move_motor();
    }

    // light_x_0
    // light_x_1
    if (device == "light") {
      light_switch();
    }

    // Z_home_0
    if (command == "home") {
      home_axis();
    }
  }
}




void home_axis() {
  Serial.print("Homing ");
  Serial.print(device);
  Serial.println(" axis...");

  define_motor_pins();

  // enable motor
  digitalWrite(ENABLE_PIN, LOW);
  delayMicroseconds(100);

  // home towards endstop direction
  digitalWrite(DIR_PIN, HIGH);  // left

  steps = 0;

  // run motor
  while (1) {
    if (digitalRead(MIN_PIN) == 0) {
      break;
    }
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(1000);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(1000);
    steps++;
  }

  // disable motor
  // digitalWrite(ENABLE_PIN, HIGH);

  // message end of action
  Serial.println(steps);
}


// read serial input
void read_serial() {
  device = Serial.readStringUntil('_');  // writes in the string all the inputs till a comma
  Serial.read();
  command = Serial.readStringUntil('_');
  Serial.read();
  String number_str = Serial.readStringUntil('\n');  // writes in the string all the inputs till the end of line character
  steps = number_str.toFloat();
}



// MOTOR COMMANDS
// move axis
void move_motor() {
  define_motor_pins();

  // enable motor
  digitalWrite(ENABLE_PIN, LOW);
  delayMicroseconds(100);

  // check if right or left movement i desired
  if (command == "L") {
    digitalWrite(DIR_PIN, HIGH);  // left
  } else if (command == "R") {
    digitalWrite(DIR_PIN, LOW);  // right
  }

  // run motor
  for (int step = 1; step <= steps; step++) {
    if (digitalRead(MIN_PIN) == 1) {
      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(1000);
      digitalWrite(STEP_PIN, LOW);
      delayMicroseconds(1000);
      status = 0;
    } else {
      Serial.print("limit ");
      Serial.print(device);
      Serial.println(" reached.");
      status = 1;
      break;
    }
  }

  // disable motor
  // digitalWrite(ENABLE_PIN, HIGH);

  // message end of action
  Serial.println(status);
}



// LIGHT COMMANDS
void light_switch() {
  if (steps == 1) {
    Serial.println("Light on.");
    digitalWrite(LIGHT_PIN, HIGH);
  } else {
    digitalWrite(LIGHT_PIN, LOW);
    Serial.println("Light off.");
  }
  Serial.println(0);
}



// MOTOR PIN DEFINITIONS
void define_motor_pins() {
  // find wich motor to move
  if (device == "X") {
    STEP_PIN = 54;
    DIR_PIN = 55;
    ENABLE_PIN = 38;
    MIN_PIN = 3;
  } else if (device == "Y") {
    STEP_PIN = 60;
    DIR_PIN = 61;
    ENABLE_PIN = 56;
    MIN_PIN = 14;
  } else if (device == "Z") {
    STEP_PIN = 46;
    DIR_PIN = 48;
    ENABLE_PIN = 62;
    MIN_PIN = 18;
  } else if (device == "E") {
    STEP_PIN = 26;
    DIR_PIN = 28;
    ENABLE_PIN = 24;
    MIN_PIN = 2;
  } else if (device == "Q") {
    STEP_PIN = 36;
    DIR_PIN = 34;
    ENABLE_PIN = 30;
    MIN_PIN = 15;
  }
}

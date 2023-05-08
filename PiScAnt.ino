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
  pinMode(X_MIN_PIN, INPUT);
  pinMode(Y_MAX_PIN, INPUT);

  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);
  pinMode(Y_MIN_PIN, INPUT);
  pinMode(Y_MAX_PIN, INPUT);

  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);
  pinMode(Z_MIN_PIN, INPUT);
  pinMode(Z_MAX_PIN, INPUT);

  pinMode(E_STEP_PIN, OUTPUT);
  pinMode(E_DIR_PIN, OUTPUT);
  pinMode(E_ENABLE_PIN, OUTPUT);

  pinMode(Q_STEP_PIN, OUTPUT);
  pinMode(Q_DIR_PIN, OUTPUT);
  pinMode(Q_ENABLE_PIN, OUTPUT);

  // disable all motors
  digitalWrite(X_ENABLE_PIN, HIGH);
  digitalWrite(Y_ENABLE_PIN, HIGH);
  digitalWrite(Z_ENABLE_PIN, HIGH);
  digitalWrite(E_ENABLE_PIN, HIGH);
  digitalWrite(Q_ENABLE_PIN, HIGH);

  Serial.begin(9600);
  Serial.println("Arduino is ready to receive on Baud 9600...");
}

// X <- test settings
float pitch_X = 4;          // mm per revolution
float microstepping_X = 2;  // 1 0 0
float steps_per_rev_X = 200 * microstepping_X;

// Y <- not yet set
float pitch_Y = 4;          // mm per revolution
float microstepping_Y = 8;  // 1 1 0
float steps_per_rev_Y = 200 * microstepping_Y;

// Z
float pitch_Z = 4;          // mm per revolution
float microstepping_Z = 1;  // 0 0 0
float steps_per_rev_Z = 200 * microstepping_Z;

int overall_X;
int overall_Y;
int overall_Z;


float steps;

// Serial inputs
String device;
String command;
float number;
int status;


void loop() {

  if (Serial.available() > 0) {
    read_serial();

    // X_R_4
    if (device == "X") {
      move_x();
    }

    // Y_R_4
    if (device == "Y") {
    }

    // Z_R_4
    if (device == "Z") {
      move_z();
    }


    // light_x_0
    // light_x_1
    if (device == "light") {
      light_switch();
    }

    // limit_x_0
    if (device == "Z" && command == "home") {
      home_Z();
    }
  }
}

void home_Z() {
  Serial.println("Homing Z axis...");
  while (digitalRead(Z_MAX_PIN) == 0) {
    number = 0.1;
    move_x();
  }
  // while (val != 0) {
  //   Serial.println("pressed");
  //   delay(0.5);
  // }
  // while (val == 0) {
  //   Serial.println("not pressed");
  //   delay(0.5);
  // }
}

// void test_limit_Z() {
//   while (1) {
//     float val = digitalRead(Z_MAX_PIN);
//     Serial.println(val);
//     delay(500);
//   }
//   // while (val != 0) {
//   //   Serial.println("pressed");
//   //   delay(0.5);
//   // }
//   // while (val == 0) {
//   //   Serial.println("not pressed");
//   //   delay(0.5);
//   // }
// }

void read_serial() {
  device = Serial.readStringUntil('_');  // writes in the string all the inputs till a comma
  Serial.read();
  command = Serial.readStringUntil('_');
  Serial.read();
  String number_str = Serial.readStringUntil('\n');  // writes in the string all the inputs till the end of line character
  number = number_str.toFloat();

  Serial.println("You sent me: ");
  Serial.println(device);
  Serial.println(command);
  Serial.println(number);
}

// MOTOR COMMANDS
void move_x() {
  // check if right or left movement i desired
  if (command == "L") {
    digitalWrite(X_DIR_PIN, HIGH);  // left
    overall_Z = overall_X - steps;
  } else if (command == "R") {
    digitalWrite(X_DIR_PIN, LOW);  // right
    overall_Z = overall_X + steps;
  }

  // calculate how many steps are needed to rech the distances in mm (=number)
  steps = number / pitch_X * steps_per_rev_X;


  // print steps
  Serial.print("number: ");
  Serial.println(number);
  Serial.print("pitch: ");
  Serial.println(pitch_X);
  Serial.print("steps: ");
  Serial.println(steps);
  steps = round(steps);
  Serial.print("steps rounded: ");
  Serial.println(steps);

  // enable motor
  digitalWrite(X_ENABLE_PIN, LOW);
  delayMicroseconds(100);

  // run motor
  for (int step = 1; step <= steps; step++) {
    if (digitalRead(X_MIN_PIN) == 1) {
      digitalWrite(X_STEP_PIN, HIGH);
      delayMicroseconds(1000);
      digitalWrite(X_STEP_PIN, LOW);
      delayMicroseconds(1000);
      status = 0;
    } else {
      Serial.println("limit X reached.");
      status = 1;
      break;
    }
  }

  // disable motor
  digitalWrite(X_ENABLE_PIN, HIGH);

  // message end of action
  Serial.println(status);
}

void move_z() {
  // check if right or left movement i desired
  if (command == "L") {
    digitalWrite(Z_DIR_PIN, HIGH);  // left
    overall_Z = overall_Z - steps;
  } else if (command == "R") {
    digitalWrite(Z_DIR_PIN, LOW);  // right
    overall_Z = overall_Z - steps;
  }

  // calculate how many steps are needed to rech the distances in mm (=number)
  steps = number / pitch_Z * steps_per_rev_Z;

  // print steps
  Serial.print("number: ");
  Serial.println(number);
  Serial.print("pitch: ");
  Serial.println(pitch_Z);
  Serial.print("steps: ");
  Serial.println(steps);
  steps = round(steps);
  Serial.print("steps rounded: ");
  Serial.println(steps);

  // enable motor
  digitalWrite(Z_ENABLE_PIN, LOW);
  delayMicroseconds(100);

  // run motor
  for (int step = 1; step <= steps; step++) {
    if (digitalRead(Z_MIN_PIN) == 1) {
      digitalWrite(Z_STEP_PIN, HIGH);
      delayMicroseconds(1000);
      digitalWrite(Z_STEP_PIN, LOW);
      delayMicroseconds(1000);
      status = 0;
    } else {
      Serial.println("limit Z reached.");
      status = 1;
      break;
    }
  }

  // disable motor
  digitalWrite(Z_ENABLE_PIN, HIGH);

  // message end of action
  Serial.println(status);
}

// LIGHT COMMANDS
void light_switch() {
  if (number == 1) {
    Serial.println("Light on.");
    digitalWrite(LIGHT_PIN, HIGH);
  } else {
    digitalWrite(LIGHT_PIN, LOW);
    Serial.println("Light off.");
  }
  Serial.println(0);
}

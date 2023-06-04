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

// Calculate based on max input size expected for one command
#define INPUT_SIZE 15

void setup() {

  pinMode(FAN_PIN, OUTPUT);
  pinMode(HEATER_0_PIN, OUTPUT);
  pinMode(LIGHT_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(X_MIN_PIN, INPUT_PULLUP); // not needed

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

  // deactivate all motors
  digitalWrite(X_ENABLE_PIN, HIGH);
  digitalWrite(Y_ENABLE_PIN, HIGH);
  digitalWrite(Z_ENABLE_PIN, HIGH);
  digitalWrite(E_ENABLE_PIN, HIGH);
  digitalWrite(Q_ENABLE_PIN, HIGH);

  Serial.begin(9600);
  delay(1000);
  // Serial.println("Arduino is ready to receive on Baud 9600...");
}

int steps;

// Serial inputs
String device;
String command;
byte status;
byte pressed = 1; // the pressed state pullup value for endstops when they're pressed
byte not_pressed = 0; // the non-pressed state 

int STEP_PIN;
int DIR_PIN;
int ENABLE_PIN;
int MIN_PIN;
int MAX_PIN;

int delay_motor;

void loop() {
  if (Serial.available() > 0) {
    read_serial();

    // X_R_100
    // Y_R_100
    // Z_R_100
    // E_R_100
    // Q_R_100
    if (device == "X" | device == "Y" | device == "Z" | device == "E" | device == "Q") {
      move_motor();
    }

    // light_x_0
    // light_x_1
    if (device == "light") {
      light_switch();
    }

    // Z_home_x
    if (command == "home") {
      home_axis();
    }

    // x_deactivate_x
    if (command == "deactivate") {
      deactivate_motors();
    }

    // x_activate_x
    if (command == "activate") {
      activate_motors();
    }
  }
}


void home_axis() {
  // Serial.print("Homing ");
  // Serial.print(device);
  // Serial.println(" axis...");

  define_motor_pins();

  // enable motor
  digitalWrite(ENABLE_PIN, LOW);
  // delayMicroseconds(100);

  // home towards endstop direction
  digitalWrite(DIR_PIN, HIGH);  // left

  steps = 0;

  // run motor
  while (1) {
    if (digitalRead(MIN_PIN) == pressed) {
      // Serial.println("Home reached.");
      break;
    }
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(delay_motor);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(delay_motor);
    steps++;
  }

  // deactivate motor
  // digitalWrite(ENABLE_PIN, HIGH);

  // message end of action
  //// Serial.println(steps);
  Serial.println(2); // 2 because move_motor() already prints out 0 or 1
}

// read serial input
void read_serial() {
  String input = Serial.readStringUntil('\n');
  
  device = getValue(input, '_', 0);
  command = getValue(input, '_', 1);
  String number_str = getValue(input, '_', 2);
  steps = number_str.toFloat();
  
  // Serial.println("device: " + device);
  // Serial.println("command: " + command);
  // Serial.println("steps: " + steps);
}

String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

// MOTOR COMMANDS
// move axis
void move_motor() {
  define_motor_pins();

  // enable motor
  digitalWrite(ENABLE_PIN, LOW);
  delayMicroseconds(delay_motor);

  // check if right or left movement i desired
  if (command == "L") {
    digitalWrite(DIR_PIN, HIGH);  // left
  } else if (command == "R") {
    digitalWrite(DIR_PIN, LOW);  // right
  }

  // run motor X_R_100
  int max_acc_steps = 15;
  if(max_acc_steps > steps/2){
    max_acc_steps = round(steps/2);
  }
  int min_delay_motor = delay_motor;
  int start_delay_motor = 1.5*delay_motor;
  int delay_change = round((start_delay_motor-min_delay_motor)/max_acc_steps);
  int curr_delay_motor = start_delay_motor;
  
  for (int step = 1; step <= steps; step++) {
    Serial.println(curr_delay_motor);
    if(step <= max_acc_steps){
      curr_delay_motor -= delay_change;
      if(curr_delay_motor < min_delay_motor){
       curr_delay_motor = min_delay_motor;
      }
    }
    else if(step >= (steps-max_acc_steps)){
      curr_delay_motor += delay_change;
      if(curr_delay_motor > start_delay_motor){
       curr_delay_motor = start_delay_motor;
      }
    }

    if (digitalRead(MIN_PIN) == not_pressed) {

      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(curr_delay_motor);
      digitalWrite(STEP_PIN, LOW);
      delayMicroseconds(curr_delay_motor);
      status = 0;
    } else {
      // Serial.print("limit ");
      // Serial.print(device);
      // Serial.println(" reached.");
      status = 1;
      break;
    }
  }

  // deactivate motor
  // digitalWrite(ENABLE_PIN, HIGH);

  // message end of action
  Serial.println(status);
}

void deactivate_motors() {
  // Serial.println("deactivating all motors...");
  digitalWrite(X_ENABLE_PIN, HIGH);
  digitalWrite(Y_ENABLE_PIN, HIGH);
  digitalWrite(Z_ENABLE_PIN, HIGH);
  digitalWrite(E_ENABLE_PIN, HIGH);
  digitalWrite(Q_ENABLE_PIN, HIGH);
  Serial.println(0);
}

void activate_motors() {
  // Serial.println("activating all motors...");
  digitalWrite(X_ENABLE_PIN, LOW);
  digitalWrite(Y_ENABLE_PIN, LOW);
  digitalWrite(Z_ENABLE_PIN, LOW);
  digitalWrite(E_ENABLE_PIN, LOW);
  digitalWrite(Q_ENABLE_PIN, LOW);
  Serial.println(0);
}

// LIGHT COMMANDS
void light_switch() {
  if (steps == 1) {
    // Serial.println("Light on.");
    digitalWrite(LIGHT_PIN, HIGH);
  } else {
    digitalWrite(LIGHT_PIN, LOW);
    // Serial.println("Light off.");
  }
  Serial.println(0);
}



// MOTOR PIN DEFINITIONS
void define_motor_pins() {
  // Serial.println(device);

  // find wich motor to move
  if (device == "X") {
    // Serial.println("motor: X");
    STEP_PIN = 54;
    DIR_PIN = 55;
    ENABLE_PIN = 38;
    MIN_PIN = 3;
    delay_motor = 4000;
  } else if (device == "Y") {
    // Serial.println("motor: Y");
    STEP_PIN = 60;
    DIR_PIN = 61;
    ENABLE_PIN = 56;
    MIN_PIN = 14;
    delay_motor = 4000;
  } else if (device == "Z") {
    // Serial.println("motor: Z");
    STEP_PIN = 46;
    DIR_PIN = 48;
    ENABLE_PIN = 62;
    MIN_PIN = 18;
    delay_motor = 750;
  } else if (device == "E") {
    // Serial.println("motor: E");
    STEP_PIN = 26;
    DIR_PIN = 28;
    ENABLE_PIN = 24;
    MIN_PIN = 2;
    delay_motor = 1000;
  } else if (device == "Q") {
    // Serial.println("motor: Q");
    STEP_PIN = 36;
    DIR_PIN = 34;
    ENABLE_PIN = 30;
    MIN_PIN = 15;
    delay_motor = 1000;
  }
}

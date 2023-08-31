import serial
import tkinter as tk
import time
from picamera2 import Picamera2, Preview
from picamera2.controls import Controls
import os
import datetime
import matplotlib.pyplot as plt
import numpy as np

# ~ Serial communication   
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5) # Replace with the correct port name and baud rate
time.sleep(1)
ser.reset_input_buffer()

# ~ Picamera intialisation
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
capture_config = picam2.create_still_configuration()


# ~ microstepping
microstepping_X = 8 # 110
microstepping_Y = 8 # 110
microstepping_Z = 4 # 010
microstepping_E = 1 # 000
microstepping_Q = 1 # 000

# ~ steps per revolution
steps_per_rev_X = 200 * microstepping_X
steps_per_rev_Y = 200 * microstepping_Y
steps_per_rev_Z = 200 * microstepping_Z
steps_per_rev_E = 200 * microstepping_E
steps_per_rev_Q = 200 * microstepping_Q

# ~ lead in mm
lead_Z = 4 # mm/rev
lead_E = 0.7 # mm/rev
lead_Q = 0.7 # mm/rev

# ~ steps per mm
steps_per_mm_Z = round(1/lead_Z * steps_per_rev_Z)
steps_per_mm_E = round(1/lead_E * steps_per_rev_E)
steps_per_mm_Q = round(1/lead_Q * steps_per_rev_Q)

# ~ initial motor step settings
X_total = 0
X_0 = 0
X_90 = 0

Y_total = 0
Y_m45 = 0
Y_0 = 0
Y_p45 = 0


Z_total = 0
Z_min_m45 = 0
Z_max_m45 = 0
Z_min_m0 = 0
Z_max_m0 = 0
Z_min_p45 = 0
Z_max_p45 = 0

E_total = 0
E_min_m45 = 0
E_max_m45 = 0
E_min_m0 = 0
E_max_m0 = 0
E_min_p45 = 0
E_max_p45 = 0

Q_total = 0
Q_min_m45 = 0
Q_max_m45 = 0
Q_min_m0 = 0
Q_max_m0 = 0
Q_min_p45 = 0
Q_max_p45 = 0

# ~ set initial number of iterations
iterations_start_X = 8
iterations_start_Y = 3
iterations_start_Z = 2

# ~ make initial number also current number that may be overwritten by user in process
X_increments = iterations_start_X
Y_increments = iterations_start_Y
Z_increments = iterations_start_Z

# ~ FUNCTIONS
def set_iterations(X_it=2, Y_it=2, Z_it=2, E_it=2, Q_it=2):
    global X_increments
    X_increments = int(X_it)
    X_it_text.set(X_it)
    global Y_increments
    Y_increments = int(Y_it)
    Y_it_text.set(Y_it)
    global Z_increments
    Z_increments = int(Z_it)
    Z_it_text.set(Z_it)
    
    
    print("*****************")
    print("X iterations: " + str(X_increments))
    print("Y iterations: " + str(Y_increments))
    print("Z iterations: " + str(Z_increments))
    print("E (=X) iterations: " + str(X_increments))
    print("Q (=X) iterations: " + str(X_increments))
    print("*****************")
    
def move_motor(motor, direction, step_type, steps=0):
    global X_total
    global Y_total
    global Z_total
    global E_total
    global Q_total
    
    X_homed = "1"
    Y_homed = "1"
    Z_homed = "1"
    E_homed = "1"
    Q_homed = "1"
    
    # Get values from input fields
    if(motor == "X"):
        if(X_homed == "1"):
            entry = entry_X.get()
            if(step_type == "unit"):
                # ~ print("in motor def unit:")
                steps = round((int(entry)-0) * (steps_per_rev_X/360))
                # ~ print(steps)
            elif(step_type == "steps"):
                # ~ print("in motor def steps:")
                steps = steps
                # ~ print(steps)
            input_value = str(steps)
            # ~ print(input_value)
            if(direction == "R"):
                X_total = X_total + steps
            elif(direction == "L"):
                X_total = X_total - steps
        else:
            print("Please home motor X first.")
            return()
        
    elif (motor == "Y"):
        if(Y_homed == "1"):
            entry = entry_Y.get()
            if(step_type == "unit"):
                steps = round((int(entry)-0) * (steps_per_rev_Y/360))
            elif(step_type == "steps"):
                steps = steps
            input_value = str(steps)
            if(direction == "R"):
                Y_total = Y_total + steps
            elif(direction == "L"):
                Y_total = Y_total - steps
        else:
            print("Please home motor Y first.")
            return()
    elif (motor == "Z"):
        # print("Z = " + Z_homed)
        if(Z_homed == "1"):
            entry = entry_Z.get()
            if(step_type == "unit"):
                steps = round((int(entry)-0)/1000 * (steps_per_mm_Z))
            elif(step_type == "steps"):
                steps = steps
            input_value = str(steps)
            if(direction == "R"):
                Z_total = Z_total + steps
            elif(direction == "L"):
                Z_total = Z_total - steps
        else:
            print("Please home motor Z first.")
            return()
    elif (motor == "E"):
        if(E_homed == "1"):
            entry = entry_E.get()
            if(step_type == "unit"):
                steps = round((int(entry)-0)/1000 * (steps_per_mm_E))
            elif(step_type == "steps"):
                steps = steps
            input_value = str(steps)
            if(direction == "R"):
                E_total = E_total + steps
            elif(direction == "L"):
                E_total = E_total - steps
            # ~ print("Current E positon (move_motor): " + str(E_total))
        else:
            print("Please home motor E first.")
            return()
    elif (motor == "Q"):
        if(Q_homed == "1"):
            entry = entry_Q.get()
            if(step_type == "unit"):
                steps = round((int(entry)-0)/1000 * (steps_per_mm_Q))
            elif(step_type == "steps"):
                steps = steps
            input_value = str(steps)
            if(direction == "R"):
                Q_total = Q_total + steps
            elif(direction == "L"):
                Q_total = Q_total - steps
        else:
            print("Please home motor Q first.")
            return()
        
    # combine value to string to send to Arduino
    send_string = motor + "_" + direction + "_" + input_value + "\n"
    # print("serial command: " + send_string.rstrip())
    
    # Send command to Arduino
    ser.write(str(send_string).encode())    
    
    while(1):
        line = ser.readline().decode('ascii').rstrip()
        # print(line)
        if(line == "0" or line == "1"):
            return
        time.sleep(0.01)

def deactivate_motors():
    send_string = "x_deactivate_x" + "\n"
    print("serial command: " + send_string)
    
    # Send command to Arduino
    ser.write(str(send_string).encode())
    
    # flush input buffer
    ser.reset_input_buffer()
    
    
    while(1):
        line = ser.readline().decode('ascii').rstrip()
        if(line == "0"):
            print("exit status: " + line)
            return
        time.sleep(0.01)
        
def activate_motors():
    send_string = "x_activate_x" + "\n"
    
    # Send command to Arduino
    #print("sending serial command: " + send_string)
    print("serial command: " + send_string)
    ser.write(str(send_string).encode())
    
    # print("serial command sent: " + send_string)
    
    # flush input buffer
    ser.reset_input_buffer()
    
    # flush input buffer
    ser.reset_input_buffer()
    
    while(1):
        # print("reading serial")
        line = ser.readline().decode('ascii').rstrip()
        if(line == "0"):
            print("exit status: " + line)
            return
        time.sleep(0.01)
    
def get_project_name():
    global project_name
    project_name = str(entry_project.get())

def create_project():
    get_project_name()
    
    # create project directory
    os.makedirs(project_name, exist_ok=True) # , exist_ok=True

def start_camera():
    print("Starting camera and preview...")
    picam2.start_preview(Preview.QTGL)
    picam2.configure(preview_config)

    picam2.start()
    time.sleep(1)

def set_camera():
    global exposure
    global gain
    exposure = (int(entry_exposure.get())-0) *1000
    gain = int(entry_gain.get())-0
    print("setting camera to ", exposure, " ", gain)
        
    ctrls = Controls(picam2)
    ctrls.AnalogueGain = gain
    ctrls.ExposureTime = exposure
    picam2.set_controls(ctrls)

    print("waiting for 1 second to apply camera settings...")
    time.sleep(1)


def take_picture(state = "scan", pos = ""):
    # set_camera()
    get_project_name()
    
    # create specimen directory and define image name
    if(state == "preview"):
        os.makedirs(project_name + "/previews/", exist_ok=True) # , exist_ok=True
        # get current time
        curr_time = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        curr_image_name = './' + project_name +'/previews/' + curr_time + '.jpg'
    
    elif(state == "scan"):
        os.makedirs(project_name + "/scan/", exist_ok=True) # , exist_ok=True
        curr_image_name = './' + project_name +'/scan/' + pos + "_" + str(exposure/1000000) + '_' + str(gain) + '.jpg'
        
    #save the picture
    print("********************** taking picture...")
    # set a trap and redirect stdout
    # trap = io.StringIO()
    # with redirect_stdout(trap):
    picam2.switch_mode_and_capture_file(capture_config, curr_image_name)
    
    # wait tuill picture is saved
    print("looking for file " + curr_image_name + "...")
    while(1):
        file_present = os.path.isfile(curr_image_name)
        if(file_present == True):
            print("file " + curr_image_name + "exists!")
            delay_after_pic = 0 # exposure/1000000
            print("delaying for " + str(delay_after_pic) + " seconds...")
            time.sleep(delay_after_pic)
            print("exit status: " + "0")
            print("**********************")
            return
            
def start_scan():
    print("****************")
    print("Scan process initalized.")
    
    global X_total
    global Y_total
    global Z_total
    global E_total
    global Q_total
    
    print("****************")
    print("Calculating steps")
    # X
    X_steps_scan = X_max-X_min
    X_steps_per_increment = round(X_steps_scan/(X_increments-1))
    print(str(X_steps_per_increment) + " per " + str(X_increments) + " increments")
    
    # Y
    Y_steps_scan = Y_p45-Y_m45
    Y_steps_per_increment = round(Y_steps_scan/(Y_increments-1))
    print(str(Y_steps_per_increment) + " per " + str(Y_increments) + " increments")
    
    # initiate plot
    plt.figure(figsize = (12,6))
    
    # Z
    Z_steps_scan = Z_p45-Z_m45
    Z_steps_per_increment = round(Z_steps_scan/(Z_increments-1))
    print(str(Z_steps_per_increment) + " per " + str(Z_increments) + " increments")

    
    # E sinus calculations
    E_steps_scan_m45 = E_max_m45-E_min_m45
    
    # print(str(E_steps_per_increment) + " per " + str(E_increments) + " increments")
    E_increments = X_increments 
    E_x_sin_m45 = np.linspace(0.5*np.pi, 2.5*np.pi, E_increments) # np.linspace(0, 2*np.pi, X_increments)
    E_y_sin_m45 = np.sin(E_x_sin_m45) * E_steps_scan_m45
    print(E_increments)
    #print("E_y_sin_m45")
    #print(E_y_sin_m45)
    
    
    plt.ion()
    plt.subplot(332)
    plt.plot(E_x_sin_m45, E_y_sin_m45)
    
    E_y_sin_m45_steps = [j-i for i, j in zip(E_y_sin_m45[:-1], E_y_sin_m45[1:])]
    E_y_sin_m45_steps.append(E_y_sin_m45_steps[0])
    E_y_sin_m45_steps = [x / 2 for x in E_y_sin_m45_steps]
    #print("E_y_sin_m45_steps")
    #print(E_y_sin_m45_steps)
        
    plt.plot(E_x_sin_m45, [x * (2) for x in E_y_sin_m45_steps])
    plt.show()
    
       
    # Q sinus calculations
    Q_steps_scan_m45 = Q_max_m45-Q_min_m45
    
    # print(str(Q_steps_per_increment) + " per " + str(Q_increments) + " increments")
    Q_increments = X_increments 
    Q_x_sin_m45 = np.linspace(0*np.pi, 2*np.pi, Q_increments) # np.linspace(0, 2*np.pi, X_increments)
    Q_y_sin_m45 = np.sin(Q_x_sin_m45) * Q_steps_scan_m45
    #print("Q_y_sin_m45")
    #print(Q_y_sin_m45)
    
    plt.subplot(333)
    plt.plot(Q_x_sin_m45, Q_y_sin_m45)
    
    
    Q_y_sin_m45_steps = [j-i for i, j in zip(Q_y_sin_m45[:-1], Q_y_sin_m45[1:])]
    Q_y_sin_m45_steps.append(Q_y_sin_m45_steps[0])
    Q_y_sin_m45_steps = [x / (-2) for x in Q_y_sin_m45_steps]
    #print("Q_y_sin_m45_steps")
    #print(Q_y_sin_m45_steps)
        
    plt.plot(Q_x_sin_m45, [x * (2) for x in Q_y_sin_m45_steps])
    plt.show()
    plt.pause(1)
    
    
    time.sleep(2)
    # move motors back to its minimum
    # move_motors_to_start(motors = "all_motors")    
    print("****************")
    
    # move all motors to start
    print("Moving all motors to start position.")
    move_motor(motor = "X", direction = "L", step_type = "steps", steps = int(X_total - X_0))
    move_motor(motor = "Y", direction = "L", step_type = "steps", steps = int(Y_total - Y_0))
    move_motor(motor = "Z", direction = "L", step_type = "steps", steps = int(Z_total - Z_min_m45))
    move_motor(motor = "E", direction = "L", step_type = "steps", steps = int(E_total - E_min_m45))
    move_motor(motor = "Q", direction = "L", step_type = "steps", steps = int(Q_total - Q_min_m45))
    
    time.sleep(2)
    
    e = 0
    q = 0
    
    
    print("****************")
    
    print("Starting scan!")
    for y in range(Y_increments):
        for x in range(X_increments):
            e = x
            # ~ print(e)
            E = round(E_y_sin_m45_steps[e])
            if(E >= 0):
                E_dir = "L"
            if(E <= 0):
                E_dir = "R"
            E = abs(E)
            # ~ print(E)
            
            q = x
            Q = round(Q_y_sin_m45_steps[e])
            if(Q >= 0):
                Q_dir = "L"
            if(Q <= 0):
                Q_dir = "R"
            Q = abs(Q)
            # ~ print(Q)
            
            for z in range(Z_increments):
                
                print("X = " + str(x))
                print("Y = " + str(y))
                print("Z = " + str(z))
                print("E = " + str(e))
                print("Q = " + str(q))
                
                take_picture(state = "scan", pos = 'X'+str(x)+'_Y'+str(y)+'_Z'+str(z)+'_E'+str(e)+'_Q'+str(q))
                print("taking picture...")
                # time.sleep(1)
                
                if(z <  Z_increments-1):
                    move_motor(motor = "Z", direction = "R", step_type = "steps", steps = Z_steps_per_increment) 
                    print("dalying " + str(int(entry_delay_pics.get())-0) + " s...")
                    time.sleep((int(entry_delay_pics.get())-0))
                elif(z ==  Z_increments-1):
                    print("Resetting motor Z by " + str((Z_increments-1)*Z_steps_per_increment))
                    move_motor(motor = "Z", direction = "L", step_type = "steps", steps = int(Z_increments-1)*Z_steps_per_increment)
                    time.sleep((int(entry_delay_pics.get())-0))
                    print("****************")
            if(x <  X_increments-1):
                # ~ plt.plot(x, E)
                move_motor(motor = "X", direction = "R", step_type = "steps", steps = X_steps_per_increment) 
                
                print("**** moving E and Q")
                move_motor(motor = "E", direction = E_dir, step_type = "steps", steps = E) 
                move_motor(motor = "Q", direction = Q_dir, step_type = "steps", steps = Q) 
                print("dalying " + str(int(entry_delay_pics.get())-0) + " s...")
                time.sleep((int(entry_delay_pics.get())-0))
                
            elif(x ==  X_increments-1):                
                print("Resetting motor X by " + str((X_increments-1)*X_steps_per_increment))
                move_motor(motor = "X", direction = "L", step_type = "steps", steps = int(X_increments-1)*X_steps_per_increment)
                                
                print("Resetting motor E by " + str(E_min_m45 - E_total))
                move_motor(motor = "E", direction = "L", step_type = "steps", steps = int(E_min_m45 - E_total))
                
                print("Resetting motor Q by " + str(Q_min_m45 - Q_total))
                move_motor(motor = "Q", direction = "L", step_type = "steps", steps = int(Q_min_m45 - Q_total))
                print("dalying " + str(int(entry_delay_pics.get())-2) + " s...")
                time.sleep((int(entry_delay_pics.get())+2))
                
            
        if(y <  Y_increments-1):
            move_motor(motor = "Y", direction = "R", step_type = "steps", steps = Y_steps_per_increment)
            print("dalying " + str(int(entry_delay_pics.get())-2) + " s...")
            time.sleep((int(entry_delay_pics.get())+2))
        elif(y ==  Y_increments-1):                
            print("Resetting motor Y by " + str((Y_increments-1)*Y_steps_per_increment))
            move_motor(motor = "Y", direction = "L", step_type = "steps", steps = int(Y_increments-1)*Y_steps_per_increment)
            print("dalying " + str(int(entry_delay_pics.get())-2) + " s...")
            time.sleep((int(entry_delay_pics.get())+2))
                    
    print('Scan done!')
    
    
def set_motor(motor, X = "NA", Y = "NA"):
    # ~ get absolute positions of motors
    global X_total
    global X_0
    global X_90
    global Y_total
    global Y_m45
    global Y_0
    global Y_p45
    global Z_total
    global E_total
    global Q_total
        
    # Get values from input fields
    if(motor == "X"):
        print("Setting motor " + motor + " to " + str(0))
        X_0 = 0
        X_total = 0
        X_90 = X_total + steps_per_rev_X / 4
      
    elif(motor == "Y"):
        print("Setting motor " + motor + " to " + str(0))
        Y_total = 0
        Y_0 = 0
        Y_m45 = Y_total + steps_per_rev_Y / 8
        Y_p45 = Y_total - steps_per_rev_Y / 8
        
    elif(motor == "E"):
        global E_total
        print("Setting motor " + motor + " at X = " + X + " and Y = " + Y + " to " + str(0))
        if(X == 0):
            if(Y == -45):
                E_0_m45 = E_total
            if(Y == 0):
                E_0_m0 = E_total
            if(Y == +45):
                E_0_p45 = E_total
        
        
        
def go_to_preset(X, Y):
    
    # ~ global variables xxx: here!: Rename variables from min to 0 etc...
    global X_0
    global X_90
    global X_total
    
    global Y_m45
    global Y_0
    global Y_p45
    global Y_total
    
    global Z
    global Z_total
    global Z_min_m45
    global Z_min_m0
    global Z_min_p45
    global Z_max_m45
    global Z_max_m0
    global Z_max_p45
    
    global E_total
    global E_min_m45
    global E_min_m0
    global E_min_p45
    global E_max_m45
    global E_max_m0
    global E_max_p45
    
    global Q_total
    global Q_min_m45
    global Q_min_m0
    global Q_min_p45
    global Q_max_m45
    global Q_max_m0
    global Q_max_p45
    global curr_preset
    
    # ~ redefine current position as <>_total xxx: here!: give every setting a flag. If flag == 0, then take current total value. Else, take set value
    # ~ if(np.isnan(Z_total)):
        # ~ Z_total = 0
    # ~ if(np.isnan(E_total)):
        # ~ E_total = 0
    # ~ if(np.isnan(Q_total)):
        # ~ Q_total = 0
    
    # ~ define preset
    if(Y == -45):
        if(X == 0):
            curr_preset = "X 0 Y -45"
        elif(X == 90):
            curr_preset = "X 90 Y -45"
    elif(Y == 0):
        if(X == 0):
            curr_preset = "X 0 Y 0"
        elif(X == 90):
            curr_preset = "X 90 Y 0"
    elif(Y == +45):
        if(X == 0):
            curr_preset = "X 0 Y 45"
        elif(X == 90):
            curr_preset = "X 90 Y 45"
    print(curr_preset)
    
        
    # ~ X
    if(X == 0):
        curr_x_steps = X_total - X_0
        curr_motor = "X"
        
        if(curr_x_steps < 0):
            curr_x_steps = abs(curr_x_steps)
            curr_direction = "R"
        else:
            curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_x_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = round(curr_x_steps)) 
        
    elif(X == 90): 
        curr_x_steps = X_total - X_90
        curr_motor = "X"
        
        if(curr_x_steps < 0):
            curr_x_steps = abs(curr_x_steps)
            curr_direction = "R"
        else:
            curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_x_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = round(curr_x_steps)) 
        
        
        
    # ~ Y
    if(Y == -45):
        curr_y_steps = Y_total - Y_m45
        curr_motor = "Y"
        
        if(curr_y_steps < 0):
            curr_y_steps = abs(curr_y_steps)
            curr_direction = "R"
        else:
            curr_direction = "L"
        
        print("Moving " + curr_motor + " by " + str(curr_y_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_y_steps) 
        
    elif(Y == 0):
        curr_y_steps = Y_total - Y_0
        curr_motor = "Y"
        
        if(curr_y_steps < 0):
            curr_y_steps = abs(curr_y_steps)
            curr_direction = "R"
        else:
            curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_y_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_y_steps) 
        
    elif(Y == +45):
        curr_y_steps = Y_total - Y_p45
        curr_motor = "Y"
        
        if(curr_y_steps < 0):
            curr_y_steps = abs(curr_y_steps)
            curr_direction = "R"
        else:
            curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_y_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_y_steps) 
    
    
    
    # ~ Z
    print("Current Z position: " + str(Z_total))
    if(Y == -45):
        if(X == 0):
            curr_z_steps = Z_total - Z_min_m45
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        elif(X == 90):
            curr_z_steps = Z_total - Z_max_m45
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        
        print("Moving " + curr_motor + " by " + str(curr_z_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_z_steps) 
        
    elif(Y == 0):
        if(X == 0):
            curr_z_steps = Z_total - Z_min_m0
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        elif(X == 90):
            curr_z_steps = Z_total - Z_max_m0
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_z_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_z_steps) 
        
    elif(Y == +45):
        if(X == 0):
            curr_z_steps = Z_total - Z_min_p45
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        elif(X == 90):
            curr_z_steps = Z_total - Z_max_p45
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_z_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_z_steps) 
    
    
    
    # ~ E
    print("Current E position: " + str(E_total))
    if(Y == -45):
        if(X == 0):
            curr_e_steps = E_total - E_min_m45
            curr_motor = "E"
            
            if(curr_e_steps < 0):
                curr_e_steps = abs(curr_e_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        elif(X == 90):
            curr_e_steps = E_total - E_max_m45
            curr_motor = "E"
            
            if(curr_e_steps < 0):
                curr_e_steps = abs(curr_e_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        
        print("Moving " + curr_motor + " by " + str(curr_e_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_e_steps) 
        
    elif(Y == 0):
        if(X == 0):
            curr_e_steps = E_total - E_min_m0
            curr_motor = "E"
            
            if(curr_e_steps < 0):
                curr_e_steps = abs(curr_e_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        elif(X == 90):
            curr_e_steps = E_total - E_max_m0
            curr_motor = "E"
            
            if(curr_e_steps < 0):
                curr_e_steps = abs(curr_e_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_e_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_e_steps) 
        
    elif(Y == +45):
        if(X == 0):
            curr_e_steps = E_total - E_min_p45
            curr_motor = "E"
            
            if(curr_e_steps < 0):
                curr_e_steps = abs(curr_e_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        elif(X == 90):
            curr_e_steps = E_total - E_max_p45
            curr_motor = "E"
            
            if(curr_e_steps < 0):
                curr_e_steps = abs(curr_e_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_e_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_e_steps) 
        
        
        
    # ~ Q
    print("Current Q position: " + str(Q_total))
    if(Y == -45):
        if(X == 0):
            curr_q_steps = Q_total - Q_min_m45
            curr_motor = "Q"
            
            if(curr_q_steps < 0):
                curr_q_steps = abs(curr_q_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        elif(X == 90):
            curr_q_steps = Q_total - Q_max_m45
            curr_motor = "Q"
            
            if(curr_q_steps < 0):
                curr_q_steps = abs(curr_q_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        
        print("Moving " + curr_motor + " by " + str(curr_q_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_q_steps) 
        
    elif(Y == 0):
        if(X == 0):
            curr_q_steps = Q_total - Q_min_m0
            curr_motor = "Q"
            
            if(curr_q_steps < 0):
                curr_q_steps = abs(curr_q_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        elif(X == 90):
            curr_q_steps = Q_total - Q_max_m0
            curr_motor = "Q"
            
            if(curr_q_steps < 0):
                curr_q_steps = abs(curr_q_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_q_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_q_steps) 
        
    elif(Y == +45):
        if(X == 0):
            curr_q_steps = Q_total - Q_min_p45
            curr_motor = "Q"
            
            if(curr_q_steps < 0):
                curr_q_steps = abs(curr_q_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
        elif(X == 90):
            curr_q_steps = Q_total - Q_max_p45
            curr_motor = "Q"
            
            if(curr_q_steps < 0):
                curr_q_steps = abs(curr_q_steps)
                curr_direction = "R"
            else:
                curr_direction = "L"
            
        print("Moving " + curr_motor + " by " + str(curr_q_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_q_steps) 
            
            
    
    
# Create GUI
root = tk.Tk()
root.title("Motor Control")

# initializing stage values for E wut NA
E_0_m45 = np.nan
E_0_m0 = np.nan
E_0_p45 = np.nan
E_90_m45 = np.nan
E_90_m0 = np.nan
E_90_p45 = np.nan
E_total = np.nan

# tkinter text variables
# ~ E0
E_0_m45_text = tk.IntVar()
E_0_m45_text.set(E_0_m45)
E_0_m0_text = tk.IntVar()
E_0_m0_text.set(E_0_m0)
E_0_p45_text = tk.IntVar()
E_0_p45_text.set(E_0_p45)

# ~ E90
E_90_m45_text = tk.IntVar()
E_90_m45_text.set(E_90_m45)
E_90_m0_text = tk.IntVar()
E_90_m0_text.set(E_90_m0)
E_90_p45_text = tk.IntVar()
E_90_p45_text.set(E_90_p45)

# ~ define text variables
X_it_text = tk.IntVar()
X_it_text.set(X_increments)
Y_it_text = tk.IntVar()
Y_it_text.set(Y_increments)
Z_it_text = tk.IntVar()
Z_it_text.set(Z_increments)

# ~ get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# ~ calculate position x and y coordinates
width = 1000
height = 620
x = (screen_width) - (width)
y = (screen_height) - height - 50
root.geometry('%dx%d+%d+%d' % (width, height, x, y))


# Create Project
r = 0
spacer_Q = tk.Label(root, text="Project creation")
spacer_Q.grid(row=r, column=0, columnspan=2)
r = r+1
spacer_project = tk.Label(root, text="Project name:")
spacer_project.grid(row=r, column=0)
entry_project = tk.Entry(root, width=7)
new_text = "project1"
entry_project.insert(0, new_text)
entry_project.grid(row=r, column=1)
button_project = tk.Button(root, text="Create Project", command=lambda: create_project())
button_project.grid(row=r, column=2)

# Create submit button
r = 1
submit_button = tk.Button(root, text="Start Scanning!", command=start_scan)
submit_button.grid(row=r, column=5, columnspan=2)

# Camera settings
r = r+1
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=0)
r = r+1
spacer_Q = tk.Label(root, text="Camera settings")
spacer_Q.grid(row=r, column=0, columnspan=2)
r = r+1
button_start_cam = tk.Button(root, text="Start Camera", command=start_camera)
button_start_cam.grid(row=r, column=0, columnspan=1)

button_start_cam = tk.Button(root, text="Set Camera", command=set_camera)
button_start_cam.grid(row=r, column=2, columnspan=1)

button_stop_cam = tk.Button(root, text="Take Picture", command=lambda: take_picture(state = "preview"))
button_stop_cam.grid(row=r, column=3, columnspan=1)

r = r+1
spacer_Q = tk.Label(root, text='exposure (ms)')
spacer_Q.grid(row=r, column=0)
entry_exposure = tk.Entry(root, width=7)
new_text = "150"
entry_exposure.insert(0, new_text)
entry_exposure.grid(row=r, column=1)
spacer_Q = tk.Label(root, text='analogue gain')
spacer_Q.grid(row=r, column=2)
entry_gain = tk.Entry(root, width=7)
new_text = "0"
entry_gain.insert(0, new_text)
entry_gain.grid(row=r, column=3)

r = r+1
spacer_Q = tk.Label(root, text='photo delay (s)')
spacer_Q.grid(row=r, column=0)
entry_delay_pics = tk.Entry(root, width=7)
new_text = "1"
entry_delay_pics.insert(0, new_text)
entry_delay_pics.grid(row=r, column=1)

# Motor energy
r = r+1
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=0)
r = r+1
spacer_Q = tk.Label(root, text="Motor energy")
spacer_Q.grid(row=r, column=0, columnspan=2)

r = r+1
button_start_cam = tk.Button(root, text="Activate motors", command=activate_motors)
button_start_cam.grid(row=r, column=0, columnspan=2)
button_stop_cam = tk.Button(root, text="Deactivate motors", command=deactivate_motors)
button_stop_cam.grid(row=r, column=2, columnspan=2)

r = r+1
row_spacer = tk.Label(root, text="        ")


# Motor controls
r = r+1
r_motor_controls = r
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=0)
r = r+1
spacer_Q = tk.Label(root, text="Motor controls")
spacer_Q.grid(row=r, column=0, columnspan=2)

r = r+1
button_X_L = tk.Button(root, text="<<< X", command=lambda: move_motor(motor = "X", direction = "L", step_type = "unit"))
button_X_L.grid(row=r, column=0)
entry_X = tk.Entry(root, width=7)
new_text = "45"
entry_X.insert(0, new_text)
entry_X.grid(row=r, column=1)
button_X_R = tk.Button(root, text="X >>>", command=lambda: move_motor(motor = "X", direction = "R", step_type = "unit"))
button_X_R.grid(row=r, column=2)
spacer_X = tk.Label(root, text="°         ")
spacer_X.grid(row=r, column=3)

r = r+1
button_Y_L = tk.Button(root, text="<<< Y", command=lambda: move_motor(motor = "Y", direction = "L", step_type = "unit"))
button_Y_L.grid(row=r, column=0)
entry_Y = tk.Entry(root, width=7)
new_text = "10"
entry_Y.insert(0, new_text)
entry_Y.grid(row=r, column=1)
button_Y_R = tk.Button(root, text="Y >>>", command=lambda: move_motor(motor = "Y", direction = "R", step_type = "unit"))
button_Y_R.grid(row=r, column=2)
spacer_Y = tk.Label(root, text="°         ")
spacer_Y.grid(row=r, column=3)

r = r+1
button_Z_L = tk.Button(root, text="<<< Z", command=lambda: move_motor(motor = "Z", direction = "L", step_type = "unit"))
button_Z_L.grid(row=r, column=0)
entry_Z = tk.Entry(root, width=7)
new_text = "1000"
entry_Z.insert(0, new_text)
entry_Z.grid(row=r, column=1)
button_Z_R = tk.Button(root, text="Z >>>", command=lambda: move_motor(motor = "Z", direction = "R", step_type = "unit"))
button_Z_R.grid(row=r, column=2)
spacer_Z = tk.Label(root, text="um        ")
spacer_Z.grid(row=r, column=3)

r = r+1
button_E_L = tk.Button(root, text="<<< E", command=lambda: move_motor(motor = "E", direction = "L", step_type = "unit"))
button_E_L.grid(row=r, column=0)
entry_E = tk.Entry(root, width=7)
new_text = "1000"
entry_E.insert(0, new_text)
entry_E.grid(row=r, column=1)
button_E_R = tk.Button(root, text="E >>>", command=lambda: move_motor(motor = "E", direction = "R", step_type = "unit"))
button_E_R.grid(row=r, column=2)
spacer_E = tk.Label(root, text="um        ")
spacer_E.grid(row=r, column=3)

r = r+1
button_Q_L = tk.Button(root, text="<<< Q", command=lambda: move_motor(motor = "Q", direction = "L", step_type = "unit"))
button_Q_L.grid(row=r, column=0)
entry_Q = tk.Entry(root, width=7)
new_text = "1000"
entry_Q.insert(0, new_text)
entry_Q.grid(row=r, column=1)
button_Q_R = tk.Button(root, text="Q >>>", command=lambda: move_motor(motor = "Q", direction = "R", step_type = "unit"))
button_Q_R.grid(row=r, column=2)
spacer_Q = tk.Label(root, text="um        ")
spacer_Q.grid(row=r, column=3)


# Iterations
r = r+1
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=0)
r = r+1
spacer_Q = tk.Label(root, text="Iterations")
spacer_Q.grid(row=r, column=0)

# Iterations Set
set_iterations_button = tk.Button(root, text="Set", command=lambda: set_iterations(X_it=entry_X_it.get(), Y_it=entry_Y_it.get(), Z_it=entry_Z_it.get(), E_it=entry_X_it.get(), Q_it=entry_X_it.get()))
set_iterations_button.grid(row=r, column=1)

# Iterations Settings
r = r+1
spacer_Q = tk.Label(root, text="X")
spacer_Q.grid(row=r, column=0)
entry_X_it = tk.Entry(root, width=5)
new_text = str(iterations_start_X)
entry_X_it.insert(0, new_text)
entry_X_it.grid(row=r, column=1)
X_it_label = tk.Label(root, textvariable=X_it_text)
X_it_label.grid(row=r, column=2)

r = r+1
spacer_Q = tk.Label(root, text="Y")
spacer_Q.grid(row=r, column=0)
entry_Y_it = tk.Entry(root, width=5)
new_text = str(iterations_start_Y)
entry_Y_it.insert(0, new_text)
entry_Y_it.grid(row=r, column=1)
Y_it_label = tk.Label(root, textvariable=Y_it_text)
Y_it_label.grid(row=r, column=2)

r = r+1
spacer_Q = tk.Label(root, text="Z")
spacer_Q.grid(row=r, column=0)
entry_Z_it = tk.Entry(root, width=5)
new_text = str(iterations_start_Z)
entry_Z_it.insert(0, new_text)
entry_Z_it.grid(row=r, column=1)
Z_it_label = tk.Label(root, textvariable=Z_it_text)
Z_it_label.grid(row=r, column=2)

r = r+1
spacer_Q = tk.Label(root, text="E")
spacer_Q.grid(row=r, column=0)
E_it_label = tk.Label(root, textvariable=X_it_text)
E_it_label.grid(row=r, column=2)

r = r+1
spacer_Q = tk.Label(root, text="Q")
spacer_Q.grid(row=r, column=0)
Q_it_label = tk.Label(root, textvariable=X_it_text)
Q_it_label.grid(row=r, column=2)


# ~ go through stages
r = r_motor_controls
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=5)

r = r+1
spacer_Q = tk.Label(root, text="Move X and Y and set to 0")
spacer_Q.grid(row=r, column=5, columnspan=4)

r = r+1
set_X_min = tk.Button(root, text="Set X0", command=lambda: set_motor(motor = "X"))
set_X_min.grid(row=r, column=5)

r = r+1
set_X_min = tk.Button(root, text="Set Y0", command=lambda: set_motor(motor = "Y"))
set_X_min.grid(row=r, column=5)

r = r+1
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=5)

r = r+1
spacer_Q = tk.Label(root, text="Choose preset for X and Y and set Z1,Z2, E, Q")
spacer_Q.grid(row=r, column=5, columnspan=4)

r = r+1
set_Z_min_m45 = tk.Button(root, text="X0; Y-45", width = 7, command=lambda: go_to_preset(X = 0, Y = -45))
set_Z_min_m45.grid(row=r, column=5)

r = r+1
set_Z_min_m45 = tk.Button(root, text="X0; Y0", width = 7, command=lambda: go_to_preset(X = 0, Y = 0))
set_Z_min_m45.grid(row=r, column=5)

r = r+1
set_Z_min_m45 = tk.Button(root, text="X0; Y+45", width = 7, command=lambda: go_to_preset(X = 0, Y = +45))
set_Z_min_m45.grid(row=r, column=5)

r = r+1
set_Z_min_m45 = tk.Button(root, text="X90; Y-45", width = 7, command=lambda: go_to_preset(X = 90, Y = -45))
set_Z_min_m45.grid(row=r, column=5)

r = r+1
set_Z_min_m45 = tk.Button(root, text="X90; Y0", width = 7, command=lambda: go_to_preset(X = 90, Y = 0))
set_Z_min_m45.grid(row=r, column=5)

r = r+1
set_Z_min_m45 = tk.Button(root, text="X90; Y+45", width = 7, command=lambda: go_to_preset(X = 90, Y = +45))
set_Z_min_m45.grid(row=r, column=5)

root.mainloop()

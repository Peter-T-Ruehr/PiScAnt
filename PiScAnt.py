import tkinter as tk
import time
from time import sleep
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
from picamera2.controls import Controls
import os
import datetime
import matplotlib.pyplot as plt
import numpy as np

# ~ Picamera intialisation
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
capture_config = picam2.create_still_configuration()


# ~ lead in mm
# ~ lead_Z = 4 # mm/rev
# ~ lead_E = 0.7 # mm/rev
# ~ lead_Q = 0.7 # mm/rev

# ~ steps per mm
# ~ steps_per_mm_Z = round(1/lead_Z * steps_per_rev_Z)
# ~ steps_per_mm_E = round(1/lead_E * steps_per_rev_E)
# ~ steps_per_mm_Q = round(1/lead_Q * steps_per_rev_Q)

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

# ~ pin definitions
CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
SPR = 200  # steps per revolution (200 ~ 1.8°)

DIR_X = 6   # Direction GPIO Pin
STEP_X = 13  # Step GPIO Pin
SLP_X = 2    # Seep GPIO Pin
microstep_X = 1/32    # microstepping
SPR_X = SPR/microstep_X    # steps per revolution incl. microstepping

DIR_Y = 19   # Direction GPIO Pin
STEP_Y = 26  # Step GPIO Pin
SLP_Y = 3    # Seep GPIO Pin
microstep_Y = 1/32    # microstepping
SPR_Y = SPR/microstep_Y    # steps per revolution incl. microstepping

DIR_Z = 20   # Direction GPIO Pin
STEP_Z = 21  # Step GPIO Pin
SLP_Z = 4    # Seep GPIO Pin
microstep_Z = 1/2    # microstepping
SPR_Z = SPR/microstep_Z    # steps per revolution incl. microstepping


# GPIO setup
GPIO.setmode(GPIO.BCM)

GPIO.setup(DIR_X, GPIO.OUT)
GPIO.setup(STEP_X, GPIO.OUT)
GPIO.setup(SLP_X, GPIO.OUT)

GPIO.setup(DIR_Y, GPIO.OUT)
GPIO.setup(STEP_Y, GPIO.OUT)
GPIO.setup(SLP_Y, GPIO.OUT)

GPIO.setup(DIR_Z, GPIO.OUT)
GPIO.setup(STEP_Z, GPIO.OUT)
GPIO.setup(SLP_Z, GPIO.OUT)

# ~ sleep pins are active LOW - so pulling them low puts motors to sleep
GPIO.output(SLP_X, GPIO.HIGH)
GPIO.output(SLP_Y, GPIO.HIGH)
GPIO.output(SLP_Z, GPIO.LOW)

delay_X = .000025
delay_Y = .0002
delay_Z = .00025

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
   

def move_motor(motor, 
                    direction):
    
    print(motor)
    
    global X_total
    global Y_total
    global Z_total
    
    X_homed = "1"
    Y_homed = "1"
    Z_homed = "1"
    
    if(motor == "X"):
        if(X_homed == "1"):
            entry = entry_X.get()
            print(entry)
            steps = int(entry)
            # ~ steps = round(int(entry)/360 * SPR_X)
            print(steps)
            if(direction == CW):
                X_total = X_total + steps
            elif(direction == CCW):
                X_total = X_total - steps
            print(X_total)
                    
            curr_dir_pin = DIR_X
            curr_step_pin = STEP_X
            curr_slp_pin = SLP_X
            curr_delay = delay_X
        else:
            print("Please home motor X first.")
            return()

    if(motor == "Y"):
        if(Y_homed == "1"):
            entry = entry_Y.get()
            print(entry)
            steps = int(entry)
            # ~ steps = round(int(entry)/360 * SPR_Y)
            print(steps)
            if(direction == CW):
                Y_total = Y_total + steps
            elif(direction == CCW):
                Y_total = Y_total - steps
            print(Y_total)
            
            curr_dir_pin = DIR_Y
            curr_step_pin = STEP_Y
            curr_slp_pin = SLP_X
            curr_delay = delay_Y
        else:
            print("Please home motor Y first.")
            return()
            
    if(motor == "Z"):
        if(Z_homed == "1"):
            entry = entry_Z.get()
            print(entry)
            steps = int(entry)
            # ~ steps = round(int(entry)/360 * SPR_Z)
            print(steps)
            if(direction == CW):
                Z_total = Z_total + steps
            elif(direction == CCW):
                Z_total = Z_total - steps
            print(Z_total)
                    
            curr_dir_pin = DIR_Z
            curr_step_pin = STEP_Z
            curr_slp_pin = SLP_X
            curr_delay = delay_Z
            
            GPIO.output(SLP_Z, GPIO.HIGH)
            sleep(.1)
            
        else:
            print("Please home motor Z first.")
            return()
    
    GPIO.output(curr_dir_pin, direction)
    for x in range(steps):
        GPIO.output(curr_step_pin, GPIO.HIGH)
        sleep(curr_delay)
        GPIO.output(curr_step_pin, GPIO.LOW)
        sleep(curr_delay)
        
    if(motor == "Z"):
        GPIO.output(SLP_Z, GPIO.LOW)

def deactivate_motors():
    GPIO.output(SLP_X, GPIO.LOW)
    GPIO.output(SLP_Y, GPIO.LOW)
    GPIO.output(SLP_Z, GPIO.LOW)
        
def activate_motors():
    GPIO.output(SLP_X, GPIO.HIGH)
    GPIO.output(SLP_Y, GPIO.HIGH)
    GPIO.output(SLP_Z, GPIO.HIGH)
    
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
   
    
    # ~ time.sleep(2)
    # move motors back to its minimum
    # move_motors_to_start(motors = "all_motors")    
    print("****************")
    
    # move all motors to start
    print("Moving all motors to start position.")
    move_motor(motor = "X", direction = CCW, step_type = "steps", steps = int(X_total - X_0))
    move_motor(motor = "Y", direction = CCW, step_type = "steps", steps = int(Y_total - Y_0))
    move_motor(motor = "Z", direction = CCW, step_type = "steps", steps = int(Z_total - Z_min_m45))
    time.sleep(2)
       
    
    print("****************")
    
    print("Starting scan!")
    for y in range(Y_increments):
        for x in range(X_increments):
            
            for z in range(Z_increments):
                
                print("X = " + str(x))
                print("Y = " + str(y))
                print("Z = " + str(z))
                
                take_picture(state = "scan", pos = 'X'+str(x)+'_Y'+str(y)+'_Z'+str(z)+'_E'+str(e)+'_Q'+str(q))
                print("taking picture...")
                # time.sleep(1)
                
                if(z <  Z_increments-1):
                    move_motor(motor = "Z", direction = CW, step_type = "steps", steps = Z_steps_per_increment) 
                    print("dalying " + str(int(entry_delay_pics.get())-0) + " s...")
                    time.sleep((int(entry_delay_pics.get())-0))
                elif(z ==  Z_increments-1):
                    print("Resetting motor Z by " + str((Z_increments-1)*Z_steps_per_increment))
                    move_motor(motor = "Z", direction = CCW, step_type = "steps", steps = int(Z_increments-1)*Z_steps_per_increment)
                    time.sleep((int(entry_delay_pics.get())-0))
                    print("****************")
            if(x <  X_increments-1):
                # ~ plt.plot(x, E)
                move_motor(motor = "X", direction = CW, step_type = "steps", steps = X_steps_per_increment) 
                
                print("**** moving E and Q")
                move_motor(motor = "E", direction = E_dir, step_type = "steps", steps = E) 
                move_motor(motor = "Q", direction = Q_dir, step_type = "steps", steps = Q) 
                print("dalying " + str(int(entry_delay_pics.get())-0) + " s...")
                time.sleep((int(entry_delay_pics.get())-0))
                
            elif(x ==  X_increments-1):                
                print("Resetting motor X by " + str((X_increments-1)*X_steps_per_increment))
                move_motor(motor = "X", direction = CCW, step_type = "steps", steps = int(X_increments-1)*X_steps_per_increment)
                                
                print("Resetting motor E by " + str(E_min_m45 - E_total))
                move_motor(motor = "E", direction = CCW, step_type = "steps", steps = int(E_min_m45 - E_total))
                
                print("Resetting motor Q by " + str(Q_min_m45 - Q_total))
                move_motor(motor = "Q", direction = CCW, step_type = "steps", steps = int(Q_min_m45 - Q_total))
                print("dalying " + str(int(entry_delay_pics.get())-2) + " s...")
                time.sleep((int(entry_delay_pics.get())+2))
                
            
        if(y <  Y_increments-1):
            move_motor(motor = "Y", direction = CW, step_type = "steps", steps = Y_steps_per_increment)
            print("dalying " + str(int(entry_delay_pics.get())-2) + " s...")
            time.sleep((int(entry_delay_pics.get())+2))
        elif(y ==  Y_increments-1):                
            print("Resetting motor Y by " + str((Y_increments-1)*Y_steps_per_increment))
            move_motor(motor = "Y", direction = CCW, step_type = "steps", steps = int(Y_increments-1)*Y_steps_per_increment)
            print("dalying " + str(int(entry_delay_pics.get())-2) + " s...")
            time.sleep((int(entry_delay_pics.get())+2))
                    
    print('Scan done!')
    
    
# ~ def set_motor(motor, X = "NA", Y = "NA"):
    # ~ # get absolute positions of motors
    # ~ global X_total
    # ~ global X_0
    # ~ global X_90
    # ~ global Y_total
    # ~ global Y_m45
    # ~ global Y_0
    # ~ global Y_p45
    # ~ global Z_total
        
    # ~ # Get values from input fields
    # ~ if(motor == "X"):
        # ~ print("Setting motor " + motor + " to " + str(0))
        # ~ X_0 = 0
        # ~ X_total = 0
        # ~ X_90 = X_total + steps_per_rev_X / 4
      
    # ~ elif(motor == "Y"):
        # ~ print("Setting motor " + motor + " to " + str(0))
        # ~ Y_total = 0
        # ~ Y_0 = 0
        # ~ Y_m45 = Y_total + steps_per_rev_Y / 8
        # ~ Y_p45 = Y_total - steps_per_rev_Y / 8
        
        
        
        
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
            curr_direction = CW
        else:
            curr_direction = CCW
            
        print("Moving " + curr_motor + " by " + str(curr_x_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = round(curr_x_steps)) 
        
    elif(X == 90): 
        curr_x_steps = X_total - X_90
        curr_motor = "X"
        
        if(curr_x_steps < 0):
            curr_x_steps = abs(curr_x_steps)
            curr_direction = CW
        else:
            curr_direction = CCW
            
        print("Moving " + curr_motor + " by " + str(curr_x_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = round(curr_x_steps)) 
        
        
        
    # ~ Y
    if(Y == -45):
        curr_y_steps = Y_total - Y_m45
        curr_motor = "Y"
        
        if(curr_y_steps < 0):
            curr_y_steps = abs(curr_y_steps)
            curr_direction = CW
        else:
            curr_direction = CCW
        
        print("Moving " + curr_motor + " by " + str(curr_y_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_y_steps) 
        
    elif(Y == 0):
        curr_y_steps = Y_total - Y_0
        curr_motor = "Y"
        
        if(curr_y_steps < 0):
            curr_y_steps = abs(curr_y_steps)
            curr_direction = CW
        else:
            curr_direction = CCW
            
        print("Moving " + curr_motor + " by " + str(curr_y_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_y_steps) 
        
    elif(Y == +45):
        curr_y_steps = Y_total - Y_p45
        curr_motor = "Y"
        
        if(curr_y_steps < 0):
            curr_y_steps = abs(curr_y_steps)
            curr_direction = CW
        else:
            curr_direction = CCW
            
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
                curr_direction = CW
            else:
                curr_direction = CCW
        elif(X == 90):
            curr_z_steps = Z_total - Z_max_m45
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = CW
            else:
                curr_direction = CCW
        
        print("Moving " + curr_motor + " by " + str(curr_z_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_z_steps) 
        
    elif(Y == 0):
        if(X == 0):
            curr_z_steps = Z_total - Z_min_m0
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = CW
            else:
                curr_direction = CCW
        elif(X == 90):
            curr_z_steps = Z_total - Z_max_m0
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = CW
            else:
                curr_direction = CCW
            
        print("Moving " + curr_motor + " by " + str(curr_z_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_z_steps) 
        
    elif(Y == +45):
        if(X == 0):
            curr_z_steps = Z_total - Z_min_p45
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = CW
            else:
                curr_direction = CCW
        elif(X == 90):
            curr_z_steps = Z_total - Z_max_p45
            curr_motor = "Z"
            
            if(curr_z_steps < 0):
                curr_z_steps = abs(curr_z_steps)
                curr_direction = CW
            else:
                curr_direction = CCW
            
        print("Moving " + curr_motor + " by " + str(curr_z_steps))
        move_motor(motor = curr_motor, direction = curr_direction, step_type = "steps", steps = curr_z_steps) 
    
    
    
    
# Create GUI
root = tk.Tk()
root.title("Motor Control")


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
width = 600
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
button_X_L = tk.Button(root, text="<<< X", command=lambda: move_motor(motor = "X", direction = CCW))
button_X_L.grid(row=r, column=0)
entry_X = tk.Entry(root, width=7)
new_text = "6400"
entry_X.insert(0, new_text)
entry_X.grid(row=r, column=1)
button_X_R = tk.Button(root, text="X >>>", command=lambda: move_motor(motor = "X", direction = CW))
button_X_R.grid(row=r, column=2)
spacer_X = tk.Label(root, text="steps    ")
spacer_X.grid(row=r, column=3)

r = r+1
button_Y_L = tk.Button(root, text="<<< Y", command=lambda: move_motor(motor = "Y", direction = CCW))
button_Y_L.grid(row=r, column=0)
entry_Y = tk.Entry(root, width=7)
new_text = "400"
entry_Y.insert(0, new_text)
entry_Y.grid(row=r, column=1)
button_Y_R = tk.Button(root, text="Y >>>", command=lambda: move_motor(motor = "Y", direction = CW))
button_Y_R.grid(row=r, column=2)
spacer_Y = tk.Label(root, text="steps    ")
spacer_Y.grid(row=r, column=3)

r = r+1
button_Z_L = tk.Button(root, text="<<< Z", command=lambda: move_motor(motor = "Z", direction = CCW))
button_Z_L.grid(row=r, column=0)
entry_Z = tk.Entry(root, width=7)
new_text = "800"
entry_Z.insert(0, new_text)
entry_Z.grid(row=r, column=1)
button_Z_R = tk.Button(root, text="Z >>>", command=lambda: move_motor(motor = "Z", direction = CW))
button_Z_R.grid(row=r, column=2)
spacer_Z = tk.Label(root, text="steps    ")
spacer_Z.grid(row=r, column=3)



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


# ~ go through stages
r = r_motor_controls
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=5)

r = r+1
spacer_Q = tk.Label(root, text="Move X and Y and set to 0")
spacer_Q.grid(row=r, column=5, columnspan=4)

r = r+1
# ~ set_X_min = tk.Button(root, text="Set X.min", command=lambda: set_motor(motor = "X"))
# ~ set_X_min.grid(row=r, column=5)
set_Y_min = tk.Button(root, text="Set Y.min", command=lambda: set_motor(motor = "Y"))
set_Y_min.grid(row=r, column=5)
set_Y_min = tk.Button(root, text="Set Z.min", command=lambda: set_motor(motor = "Z"))
set_Y_min.grid(row=r, column=6)

r = r+1
# ~ set_X_max = tk.Button(root, text="Set X.max", command=lambda: set_motor(motor = "X"))
# ~ set_X_max.grid(row=r, column=5)
set_Y_max = tk.Button(root, text="Set Y.max", command=lambda: set_motor(motor = "Y"))
set_Y_max.grid(row=r, column=5)
set_Y_max = tk.Button(root, text="Set Z.max", command=lambda: set_motor(motor = "Z"))
set_Y_max.grid(row=r, column=6)

# ~ r = r+1
# ~ spacer_Q = tk.Label(root, text="Choose preset for X and Y and set Z1 and Z2")
# ~ spacer_Q.grid(row=r, column=5, columnspan=4)

# ~ r = r+1
# ~ set_Z_min_m45 = tk.Button(root, text="X0; Y-45", width = 7, command=lambda: go_to_preset(X = 0, Y = -45))
# ~ set_Z_min_m45.grid(row=r, column=5)

# ~ r = r+1
# ~ set_Z_min_m45 = tk.Button(root, text="X0; Y0", width = 7, command=lambda: go_to_preset(X = 0, Y = 0))
# ~ set_Z_min_m45.grid(row=r, column=5)

# ~ r = r+1
# ~ set_Z_min_m45 = tk.Button(root, text="X0; Y+45", width = 7, command=lambda: go_to_preset(X = 0, Y = +45))
# ~ set_Z_min_m45.grid(row=r, column=5)

# ~ r = r+1
# ~ set_Z_min_m45 = tk.Button(root, text="X90; Y-45", width = 7, command=lambda: go_to_preset(X = 90, Y = -45))
# ~ set_Z_min_m45.grid(row=r, column=5)

# ~ r = r+1
# ~ set_Z_min_m45 = tk.Button(root, text="X90; Y0", width = 7, command=lambda: go_to_preset(X = 90, Y = 0))
# ~ set_Z_min_m45.grid(row=r, column=5)

# ~ r = r+1
# ~ set_Z_min_m45 = tk.Button(root, text="X90; Y+45", width = 7, command=lambda: go_to_preset(X = 90, Y = +45))
# ~ set_Z_min_m45.grid(row=r, column=5)

root.mainloop()

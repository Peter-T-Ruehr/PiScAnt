import serial
import tkinter as tk
import time
from picamera2 import Picamera2, Preview
from picamera2.controls import Controls
# import io
# import sys
# from contextlib import redirect_stdout
import os
import datetime

   
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5) # Replace with the correct port name and baud rate
time.sleep(1)
ser.reset_input_buffer()

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
capture_config = picam2.create_still_configuration()

microstepping_X = 8 # 110
microstepping_Y = 8 # 110
microstepping_Z = 4 # 010
microstepping_E = 1 # 000
microstepping_Q = 1 # 000

steps_per_rev_X = 200 * microstepping_X
steps_per_rev_Y = 200 * microstepping_Y
steps_per_rev_Z = 200 * microstepping_Z
steps_per_rev_E = 200 * microstepping_E
steps_per_rev_Q = 200 * microstepping_Q

lead_Z = 4 # mm/rev
lead_E = 0.7 # mm/rev
lead_Q = 0.7 # mm/rev

steps_per_mm_Z = round(1/lead_Z * steps_per_rev_Z)
steps_per_mm_E = round(1/lead_E * steps_per_rev_E)
steps_per_mm_Q = round(1/lead_Q * steps_per_rev_Q)

iterations_start = 2

X_homed = "0"
X_min = 0
X_max = 0
X_total = 0
X_increments = iterations_start

Y_homed = "0"
Y_min = 0
Y_max = 0
Y_total = 0
Y_increments = iterations_start

Z_max_mm = 125
Z_max_steps = round(Z_max_mm* steps_per_mm_Z) # 6250
Z_homed = "0"
Z_min = 0
Z_max = 0
Z_total = 0
Z_increments = iterations_start

E_homed = "0"
E_min = 0
E_max = 0
E_total = 0
E_increments = iterations_start

Q_homed = "0"
Q_min = 0
Q_max = 0
Q_total = 0
Q_increments = iterations_start

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
            print("delaying for " + str(exposure/1000000) + " seconds...")
            time.sleep(exposure/1000000)
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
    Y_steps_scan = Y_max-Y_min
    Y_steps_per_increment = round(Y_steps_scan/(Y_increments-1))
    print(str(Y_steps_per_increment) + " per " + str(Y_increments) + " increments")
    
    # Z
    Z_steps_scan = Z_max-Z_min
    Z_steps_per_increment = round(Z_steps_scan/(Z_increments-1))
    print(str(Z_steps_per_increment) + " per " + str(Z_increments) + " increments")
    
    # E
    E_steps_scan = E_max-E_min
    E_steps_per_increment = round(E_steps_scan/(E_increments-1))
    print(str(E_steps_per_increment) + " per " + str(E_increments) + " increments")
    
    # Q
    Q_steps_scan = Q_max-Q_min
    Q_steps_per_increment = round(Q_steps_scan/(Q_increments-1))
    print(str(Q_steps_per_increment) + " per " + str(Q_increments) + " increments")
    
    time.sleep(2)
    # move motors back to its minimum
    # move_motors_to_start(motors = "all_motors")    
    print("****************")
    
    # move all motors to start
    print("Moving all motors to start position.")
    move_motor(motor = "X", direction = "L", step_type = "steps", steps = int(X_total - X_min))
    move_motor(motor = "Y", direction = "L", step_type = "steps", steps = int(Y_total - Y_min))
    move_motor(motor = "Z", direction = "L", step_type = "steps", steps = int(Z_total - Z_min))
    move_motor(motor = "E", direction = "L", step_type = "steps", steps = int(E_total - E_min))
    move_motor(motor = "Q", direction = "L", step_type = "steps", steps = int(Q_total - Q_min))
    
    time.sleep(2)
    
    e = 0
    q = 0
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
                    move_motor(motor = "Z", direction = "R", step_type = "steps", steps = Z_steps_per_increment) 
                elif(z ==  Z_increments-1):
                    print("Resetting motor Z by " + str((Z_increments-1)*Z_steps_per_increment))
                    move_motor(motor = "Z", direction = "L", step_type = "steps", steps = int(Z_increments-1)*Z_steps_per_increment)
                    print("****************")
            if(x <  X_increments-1):
                move_motor(motor = "X", direction = "R", step_type = "steps", steps = X_steps_per_increment) 
            elif(y ==  Y_increments-1):                
                print("Resetting motor X by " + str((X_increments-1)*X_steps_per_increment))
                move_motor(motor = "X", direction = "L", step_type = "steps", steps = int(X_increments-1)*X_steps_per_increment)
            
        if(y <  Y_increments-1):
            move_motor(motor = "Y", direction = "R", step_type = "steps", steps = Y_steps_per_increment)
            time.sleep(1)
        elif(y ==  Y_increments-1):                
            print("Resetting motor Y by " + str((Y_increments-1)*Y_steps_per_increment))
            move_motor(motor = "Y", direction = "L", step_type = "steps", steps = int(Y_increments-1)*Y_steps_per_increment)
            time.sleep(1)
                    
    print('Scan done!')

        
    
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
                steps = round((int(entry)-0) * (steps_per_rev_X/360))
            elif(step_type == "steps"):
                steps = steps
            input_value = str(steps)
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
    
    # print("motor " + motor + ": " + input_value)
    
    # combine value to string to send to Arduino
    send_string = motor + "_" + direction + "_" + input_value + "\n"
    print("serial command: " + send_string.rstrip())
    
    # Send command to Arduino
    ser.write(str(send_string).encode())    
    
    while(1):
        line = ser.readline().decode('ascii').rstrip()
        # print(line)
        if(line == "0" or line == "1"):
            print("exit status: " + line)
            # print(str(X_total))
            # pprint(str(Y_total))
            # pprint(str(Z_total))
            # pprint(str(E_total))
            # pprint(str(Q_total))
            return
        time.sleep(0.01)

def home_motor(motor):
    send_string = motor + "_home_0" + "\n"
    print("serial command: " + send_string)

    # Send command to Arduino
    ser.write(str(send_string).encode())
    
    # flush input buffer
    ser.reset_input_buffer()
    
    while(1):
        line = ser.readline().decode('ascii').rstrip()
        if(line == "2"):
            if(motor == "X"):
                global X_homed
                X_homed = "1"
                global X_total
                X_total = 0
                print("X homed set to " + X_homed)
            elif(motor == "Y"):
                global Y_homed
                Y_homed = "1"
                global Y_total
                Y_total = 0
                print("Y homed set to " + Y_homed)
            elif(motor == "Z"):
                global Z_homed
                Z_homed = "1"
                global Z_total
                Z_total = 0
                print("Z homed set to " + Z_homed)
            elif(motor == "E"):
                global E_homed
                E_homed = "1"
                global E_total
                E_total = 0
                print("E homed set to " + E_homed)
            elif(motor == "Q"):
                global Q_homed
                Q_homed = "1"
                global Q_total
                Q_total = 0
                print("Q homed set to " + Q_homed)
            print("exit status: " + line)
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

def set_motor(motor, direction):
    # Get values from input fields
    if(motor == "X"):
        print("Setting " + direction + " for motor " + motor + " to " + str(X_total))
        if(direction == "min"):
            global X_min
            X_min = X_total
            global X_min_text
            X_min_text.set(X_min)
        elif(direction == "max"):
            global X_max
            X_max = X_total
            global X_max_text
            X_max_text.set(X_max)
    elif(motor == "Y"):
        print("Setting " + direction + " for motor " + motor + " to " + str(Y_total))
        if(direction == "min"):
            global Y_min
            Y_min = Y_total
            global Y_min_text
            Y_min_text.set(Y_min)
        elif(direction == "max"):
            global Y_max
            Y_max = Y_total
            global Y_max_text
            Y_max_text.set(Y_max)
    elif(motor == "Z"):
        print("Setting " + direction + " for motor " + motor + " to " + str(Z_total))
        if(direction == "min"):
            global Z_min
            Z_min = Z_total
            global Z_min_text
            Z_min_text.set(Z_min)
        elif(direction == "max"):
            global Z_max
            Z_max = Z_total
            global Z_max_text
            Z_max_text.set(Z_max)
    elif(motor == "E"):
        print("Setting " + direction + " for motor " + motor + " to " + str(E_total))
        if(direction == "min"):
            global E_min
            E_min = E_total
            global E_min_text
            E_min_text.set(E_min)
        elif(direction == "max"):
            global E_max
            E_max = E_total
            global E_max_text
            E_max_text.set(E_max)
    elif(motor == "Q"):
        print("Setting " + direction + " for motor " + motor + " to " + str(Q_total))
        if(direction == "min"):
            global Q_min
            Q_min = Q_total
            global Q_min_text
            Q_min_text.set(Q_min)
        elif(direction == "max"):
            global Q_max
            Q_max = Q_total
            global Q_max_text
            Q_max_text.set(Q_max)
            
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
    global E_increments
    E_increments = int(E_it)
    E_it_text.set(E_it)
    global Q_increments
    Q_increments = int(Q_it)
    Q_it_text.set(Q_it)
    print("*****************")
    print("X iterations: " + str(X_it))
    print("Y iterations: " + str(Y_it))
    print("Z iterations: " + str(Z_it))
    print("E iterations: " + str(E_it))
    print("Q iterations: " + str(Q_it))
    print("*****************")
    
    
    
# start_camera()

# Create GUI
root = tk.Tk()
root.title("Motor Control")


X_min_text = tk.IntVar()
X_min_text.set(X_min)
X_max_text = tk.IntVar()
X_max_text.set(X_max)

Y_min_text = tk.IntVar()
Y_min_text.set(Y_min)
Y_max_text = tk.IntVar()
Y_max_text.set(Y_max)

Z_min_text = tk.IntVar()
Z_min_text.set(Z_min)
Z_max_text = tk.IntVar()
Z_max_text.set(Z_max)

E_min_text = tk.IntVar()
E_min_text.set(E_min)
E_max_text = tk.IntVar()
E_max_text.set(E_max)

Q_min_text = tk.IntVar()
Q_min_text.set(Q_min)
Q_max_text = tk.IntVar()
Q_max_text.set(Q_max)

X_it_text = tk.IntVar()
X_it_text.set(X_increments)
Y_it_text = tk.IntVar()
Y_it_text.set(Y_increments)
Z_it_text = tk.IntVar()
Z_it_text.set(Z_increments)
E_it_text = tk.IntVar()
E_it_text.set(E_increments)
Q_it_text = tk.IntVar()
Q_it_text.set(Q_increments)

# get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# calculate position x and y coordinates
width = 800
height = 700
x = (screen_width/3) - (width/2)
y = (0) - (height/2) # screen_height/2
root.geometry('%dx%d+%d+%d' % (width, height, x, y))

# Create Project
r = 0
spacer_Q = tk.Label(root, text="Project creation")
spacer_Q.grid(row=r, column=0)
r = r+1
spacer_project = tk.Label(root, text="Project name:")
spacer_project.grid(row=r, column=0)
entry_project = tk.Entry(root, width=7)
new_text = "project1"
entry_project.insert(0, new_text)
entry_project.grid(row=r, column=1)
button_project = tk.Button(root, text="Create Project", command=lambda: create_project())
button_project.grid(row=r, column=2)

# Camera settings
r = r+1
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=0)
r = r+1
spacer_Q = tk.Label(root, text="Camera settings")
spacer_Q.grid(row=r, column=0)
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

# homing
r = r+1
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=0)
r = r+1
spacer_Q = tk.Label(root, text="Homing")
spacer_Q.grid(row=r, column=0)
r = r+1
# home_X = tk.Button(root, text="Home X", command=lambda: home_motor(motor = "X"))
# home_X.grid(row=r, column=0)
home_Y = tk.Button(root, text="Home Y", command=lambda: home_motor(motor = "Y"))
home_Y.grid(row=r, column=0)
home_Z = tk.Button(root, text="Home Z", command=lambda: home_motor(motor = "Z"))
home_Z.grid(row=r, column=1)
r = r+1
home_E = tk.Button(root, text="Home E", command=lambda: home_motor(motor = "E"))
home_E.grid(row=r, column=0)
home_Q = tk.Button(root, text="Home Q", command=lambda: home_motor(motor = "Q"))
home_Q.grid(row=r, column=1)

# Motor controls
r = r+1
r_motor_controls = r
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=0)
r = r+1
spacer_Q = tk.Label(root, text="Motor controls")
spacer_Q.grid(row=r, column=0)

r = r+1
button_X_L = tk.Button(root, text="<<< X", command=lambda: move_motor(motor = "X", direction = "L", step_type = "unit"))
button_X_L.grid(row=r, column=0)
entry_X = tk.Entry(root, width=7)
new_text = "10"
entry_X.insert(0, new_text)
entry_X.grid(row=r, column=1)
button_X_R = tk.Button(root, text="X >>>", command=lambda: move_motor(motor = "X", direction = "R", step_type = "unit"))
button_X_R.grid(row=r, column=2)
spacer_X = tk.Label(root, text="°         ")
spacer_X.grid(row=r, column=3)

r = r+1
button_Y_L = tk.Button(root, text="<<< Y", command=lambda: move_motor(motor = "Y", direction = "R", step_type = "unit"))
button_Y_L.grid(row=r, column=0)
entry_Y = tk.Entry(root, width=7)
new_text = "10"
entry_Y.insert(0, new_text)
entry_Y.grid(row=r, column=1)
button_Y_R = tk.Button(root, text="Y >>>", command=lambda: move_motor(motor = "Y", direction = "L", step_type = "unit"))
button_Y_R.grid(row=r, column=2)
spacer_Y = tk.Label(root, text="°         ")
spacer_Y.grid(row=r, column=3)
r = r+1
button_Z_L = tk.Button(root, text="<<< Z", command=lambda: move_motor(motor = "Z", direction = "R", step_type = "unit"))
button_Z_L.grid(row=r, column=0)
entry_Z = tk.Entry(root, width=7)
new_text = "1000"
entry_Z.insert(0, new_text)
entry_Z.grid(row=r, column=1)
button_Z_R = tk.Button(root, text="Z >>>", command=lambda: move_motor(motor = "Z", direction = "L", step_type = "unit"))
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



# Motor ranges
r = r_motor_controls
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=4)
r = r+1
spacer_Q = tk.Label(root, text="Motor ranges")
spacer_Q.grid(row=r, column=4)
r = r+1
set_X_min = tk.Button(root, text="Set X min", command=lambda: set_motor(motor = "X", direction = "min"))
set_X_min.grid(row=r, column=4)
X_min_label = tk.Label(root, textvariable=X_min_text)
X_min_label.grid(row=r, column=5)
X_max_label = tk.Label(root, textvariable=X_max_text)
X_max_label.grid(row=r, column=6)
set_X_max = tk.Button(root, text="Set X max", command=lambda: set_motor(motor = "X", direction = "max"))
set_X_max.grid(row=r, column=7)
r = r+1
set_Y_min = tk.Button(root, text="Set Y min", command=lambda: set_motor(motor = "Y", direction = "min"))
set_Y_min.grid(row=r, column=4)
Y_min_label = tk.Label(root, textvariable=Y_min_text)
Y_min_label.grid(row=r, column=5)
Y_max_label = tk.Label(root, textvariable=Y_max_text)
Y_max_label.grid(row=r, column=6)
set_Y_max = tk.Button(root, text="Set Y max", command=lambda: set_motor(motor = "Y", direction = "max"))
set_Y_max.grid(row=r, column=7)
r = r+1
set_Z_min = tk.Button(root, text="Set Z min", command=lambda: set_motor(motor = "Z", direction = "min"))
set_Z_min.grid(row=r, column=4)
Z_min_label = tk.Label(root, textvariable=Z_min_text)
Z_min_label.grid(row=r, column=5)
Z_max_label = tk.Label(root, textvariable=Z_max_text)
Z_max_label.grid(row=r, column=6)
set_Z_max = tk.Button(root, text="Set Z max", command=lambda: set_motor(motor = "Z", direction = "max"))
set_Z_max.grid(row=r, column=7)
r = r+1
set_E_min = tk.Button(root, text="Set E min", command=lambda: set_motor(motor = "E", direction = "min"))
set_E_min.grid(row=r, column=4)
E_min_label = tk.Label(root, textvariable=E_min_text)
E_min_label.grid(row=r, column=5)
E_max_label = tk.Label(root, textvariable=E_max_text)
E_max_label.grid(row=r, column=6)
set_E_max = tk.Button(root, text="Set E max", command=lambda: set_motor(motor = "E", direction = "max"))
set_E_max.grid(row=r, column=7)
r = r+1
set_Q_min = tk.Button(root, text="Set Q min", command=lambda: set_motor(motor = "Q", direction = "min"))
set_Q_min.grid(row=r, column=4)
Q_min_label = tk.Label(root, textvariable=Q_min_text)
Q_min_label.grid(row=r, column=5)
Q_max_label = tk.Label(root, textvariable=Q_max_text)
Q_max_label.grid(row=r, column=6)
set_Q_max = tk.Button(root, text="Set Q max", command=lambda: set_motor(motor = "Q", direction = "max"))
set_Q_max.grid(row=r, column=7)


# Iterations
r = r_motor_controls
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=8)
r = r+1
spacer_Q = tk.Label(root, text="Iterations")
spacer_Q.grid(row=r, column=8)

# Set
set_iterations_button = tk.Button(root, text="Set", command=lambda: set_iterations(X_it=entry_X_it.get(), Y_it=entry_Y_it.get(), Z_it=entry_Z_it.get(), E_it=entry_E_it.get(), Q_it=entry_Q_it.get()))
set_iterations_button.grid(row=r, column=9)

# Settings
r = r+1
entry_X_it = tk.Entry(root, width=5)
new_text = str(iterations_start)
entry_X_it.insert(0, new_text)
entry_X_it.grid(row=r, column=8)
X_it_label = tk.Label(root, textvariable=X_it_text)
X_it_label.grid(row=r, column=9)


r = r+1
entry_Y_it = tk.Entry(root, width=5)
new_text = str(iterations_start)
entry_Y_it.insert(0, new_text)
entry_Y_it.grid(row=r, column=8)
Y_it_label = tk.Label(root, textvariable=Y_it_text)
Y_it_label.grid(row=r, column=9)

r = r+1
entry_Z_it = tk.Entry(root, width=5)
new_text = str(iterations_start)
entry_Z_it.insert(0, new_text)
entry_Z_it.grid(row=r, column=8)
Z_it_label = tk.Label(root, textvariable=Z_it_text)
Z_it_label.grid(row=r, column=9)

r = r+1
entry_E_it = tk.Entry(root, width=5)
new_text = str(iterations_start)
entry_E_it.insert(0, new_text)
entry_E_it.grid(row=r, column=8)
E_it_label = tk.Label(root, textvariable=E_it_text)
E_it_label.grid(row=r, column=9)

r = r+1
entry_Q_it = tk.Entry(root, width=5)
new_text = str(iterations_start)
entry_Q_it.insert(0, new_text)
entry_Q_it.grid(row=r, column=8)
Q_it_label = tk.Label(root, textvariable=Q_it_text)
Q_it_label.grid(row=r, column=9)


# Motor energy
r = r_motor_controls+7
spacer_Q = tk.Label(root, text="   ")
spacer_Q.grid(row=r, column=0)
r = r+1
spacer_Q = tk.Label(root, text="Motor energy")
spacer_Q.grid(row=r, column=0)

r = r+1
button_start_cam = tk.Button(root, text="Activate motors", command=activate_motors)
button_start_cam.grid(row=r, column=0, columnspan=2)
button_stop_cam = tk.Button(root, text="Deactivate motors", command=deactivate_motors)
button_stop_cam.grid(row=r, column=2, columnspan=2)

r = r+1
row_spacer = tk.Label(root, text="        ")
row_spacer.grid(row=r, column=1)

r = r+1


r = r+1
row_spacer = tk.Label(root, text="        ")
row_spacer.grid(row=r, column=1)

# Create submit button
r = r+2
submit_button = tk.Button(root, text="Start Scanning!", command=start_scan)
submit_button.grid(row=r, column=0, columnspan=4)

root.mainloop()

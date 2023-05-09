import serial
import tkinter as tk
import time
from picamera2 import Picamera2, Preview
import os

   
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1) # Replace with the correct port name and baud rate
ser.reset_input_buffer()

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
capture_config = picam2.create_still_configuration()


microstepping_X = 8
microstepping_Y = 8
microstepping_Z = 1
microstepping_E = 1
microstepping_Q = 1


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

max_movement_X = 360 # °
max_movement_Y = 70 # °
max_movement_Z = 150 # mm
max_movement_E = 150 # mm
max_movement_Q = 150 # mm

max_steps_X = 360 * steps_per_rev_X
max_steps_Y = 70 * steps_per_rev_Y
max_steps_Z = 150 * steps_per_mm_Z
max_steps_E = 150 * steps_per_mm_E
max_steps_Q = 150 * steps_per_mm_Q

# print(steps_per_mm_E)
# print(steps_per_rev_X)
# print(steps_per_rev_Y)
# print(steps_per_mm_Z)
# print(steps_per_mm_Q)

print(max_steps_X)
print(max_steps_Y)
print(max_steps_Z)
print(max_steps_E)
print(max_steps_Q)

def start_camera():
    picam2.start_preview(Preview.QTGL)
    picam2.configure(preview_config)
    picam2.start()

def set_camera():
    global exposure
    global gain
    exposure = (int(entry_exposure.get())-0) *1000
    gain = int(entry_gain.get())-0
    print("setting camera to ", exposure, " ", gain)
    picam2.set_controls({"ExposureTime": exposure, "AnalogueGain": gain}) # 1000000 ms = 1 s
    capture_config = picam2.create_still_configuration()
    print("waiting for 2 seconds to apply camera settings...")
    time.sleep(2)

def take_picture():
    # set_camera()
    get_project_name()
    
    # create specimen directory
    os.makedirs(project_name + "/previews/", exist_ok=True) # , exist_ok=True

    #save the picture
    curr_image_name = './' + project_name +'/previews/' + str(exposure/1000) + '_' + str(gain) + '.jpg'
    picam2.switch_mode_and_capture_file(capture_config, curr_image_name)

def stop_camera():
    picam2.close()


def move_motors():
    time.sleep(0.1)

def move_motor(motor, direction):
    
    # Get values from input fields
    if(motor == "X"):
        input_value = str(round((int(entry_X.get())-0) * (steps_per_rev_X/360)))
    elif (motor == "Y"):
        input_value = str(round((int(entry_Y.get())-0) * (steps_per_rev_Y/360)))
    elif (motor == "Z"):
        input_value = str(round((int(entry_Z.get())-0)/1000 * (steps_per_mm_Z)))
    elif (motor == "E"):
        input_value = str(round((int(entry_E.get())-0)/1000 * (steps_per_mm_E)))
    elif (motor == "Q"):
        input_value = str(round((int(entry_Q.get())-0)/1000 * (steps_per_mm_Q)))
    
    # print("motor " + motor + ": " + input_value)
    
    # combine value to string to send to Arduino
    send_string = motor + "_" + direction + "_" + input_value
    print("serial command: " + send_string)

    # Send command to Arduino
    ser.write(str(send_string).encode())
    
    while(1):
        line = ser.readline().decode('ascii').rstrip()
        if(line == "0" or line == "1"):
            print("exit status: " + line)
            return
        time.sleep(0.1)

def home_motor(motor):
    send_string = motor + "_home_0"
    print("serial command: " + send_string)

    # Send command to Arduino
    ser.write(str(send_string).encode())
    
    while(1):
        line = ser.readline().decode('ascii').rstrip()
        if(line == "2"):
            print("exit status: " + line)
            return
        time.sleep(0.1)

def get_project_name():
    global project_name
    project_name = str(entry_project.get())

def create_project():
    get_project_name()
    
    # create project directory
    os.makedirs(project_name, exist_ok=True) # , exist_ok=True

start_camera()

# Create GUI
root = tk.Tk()
root.title("Motor Control")

# Create input fields
r = 0
spacer_project = tk.Label(root, text="Project name:")
spacer_project.grid(row=r, column=0)
entry_project = tk.Entry(root, width=10)
new_text = "project1"
entry_project.insert(0, new_text)
entry_project.grid(row=r, column=1)
button_project = tk.Button(root, text="Create Project", command=lambda: create_project())
button_project.grid(row=r, column=2)

r = r+1
button_X_L = tk.Button(root, text="X left", command=lambda: move_motor(motor = "X", direction = "L"))
button_X_L.grid(row=r, column=0)
entry_X = tk.Entry(root, width=10)
new_text = "1"
entry_X.insert(0, new_text)
entry_X.grid(row=r, column=1)
button_X_R = tk.Button(root, text="X right", command=lambda: move_motor(motor = "X", direction = "R"))
button_X_R.grid(row=r, column=2)
spacer_X = tk.Label(root, text="°         ")
spacer_X.grid(row=r, column=3)
home_X = tk.Button(root, text="Home X", command=lambda: home_motor(motor = "X"))
home_X.grid(row=r, column=4)

r = r+1
button_Y_L = tk.Button(root, text="Y left", command=lambda: move_motor(motor = "Y", direction = "L"))
button_Y_L.grid(row=r, column=0)
entry_Y = tk.Entry(root, width=10)
new_text = "1"
entry_Y.insert(0, new_text)
entry_Y.grid(row=r, column=1)
button_Y_R = tk.Button(root, text="Y right", command=lambda: move_motor(motor = "Y", direction = "R"))
button_Y_R.grid(row=r, column=2)
spacer_Y = tk.Label(root, text="°         ")
spacer_Y.grid(row=r, column=3)
home_Y = tk.Button(root, text="Home Y", command=lambda: home_motor(motor = "Y"))
home_Y.grid(row=r, column=4)

r = r+1
button_Z_L = tk.Button(root, text="Z left", command=lambda: move_motor(motor = "Z", direction = "L"))
button_Z_L.grid(row=r, column=0)
entry_Z = tk.Entry(root, width=10)
new_text = "1000"
entry_Z.insert(0, new_text)
entry_Z.grid(row=r, column=1)
button_Z_R = tk.Button(root, text="Z right", command=lambda: move_motor(motor = "Z", direction = "R"))
button_Z_R.grid(row=r, column=2)
spacer_Z = tk.Label(root, text="um        ")
spacer_Z.grid(row=r, column=3)
home_Z = tk.Button(root, text="Home Z", command=lambda: home_motor(motor = "Z"))
home_Z.grid(row=r, column=4)

r = r+1
button_E_L = tk.Button(root, text="E left", command=lambda: move_motor(motor = "E", direction = "L"))
button_E_L.grid(row=r, column=0)
entry_E = tk.Entry(root, width=10)
new_text = "1000"
entry_E.insert(0, new_text)
entry_E.grid(row=r, column=1)
button_E_R = tk.Button(root, text="E right", command=lambda: move_motor(motor = "E", direction = "R"))
button_E_R.grid(row=r, column=2)
spacer_E = tk.Label(root, text="um        ")
spacer_E.grid(row=r, column=3)
home_E = tk.Button(root, text="Home E", command=lambda: home_motor(motor = "E"))
home_E.grid(row=r, column=4)

r = r+1
button_Q_L = tk.Button(root, text="Q left", command=lambda: move_motor(motor = "Q", direction = "L"))
button_Q_L.grid(row=r, column=0)
entry_Q = tk.Entry(root, width=10)
new_text = "1000"
entry_Q.insert(0, new_text)
entry_Q.grid(row=r, column=1)
button_Q_R = tk.Button(root, text="Q right", command=lambda: move_motor(motor = "Q", direction = "R"))
button_Q_R.grid(row=r, column=2)
spacer_Q = tk.Label(root, text="um        ")
spacer_Q.grid(row=r, column=3)
home_Q = tk.Button(root, text="Home Q", command=lambda: home_motor(motor = "Q"))
home_Q.grid(row=r, column=4)

# r = r+1
# button_start_cam = tk.Button(root, text="Start Camera", command=lambda: start_camera())
# button_start_cam.grid(row=r, column=0, columnspan=2)
# button_stop_cam = tk.Button(root, text="Stop Camera", command=lambda: stop_camera())
# button_stop_cam.grid(row=r, column=2, columnspan=2)

r = r+1
spacer_Q = tk.Label(root, text='exposure (ms)')
spacer_Q.grid(row=r, column=0)
entry_exposure = tk.Entry(root, width=10)
new_text = "250"
entry_exposure.insert(0, new_text)
entry_exposure.grid(row=r, column=1)
spacer_Q = tk.Label(root, text='analogue gain')
spacer_Q.grid(row=r, column=2)
entry_gain = tk.Entry(root, width=10)
new_text = "1"
entry_gain.insert(0, new_text)
entry_gain.grid(row=r, column=3)

r = r+1
button_start_cam = tk.Button(root, text="Set Camera", command=lambda: set_camera())
button_start_cam.grid(row=r, column=0, columnspan=2)
button_stop_cam = tk.Button(root, text="Take Picture", command=lambda: take_picture())
button_stop_cam.grid(row=r, column=2, columnspan=2)

# Create submit button
r = r+2
submit_button = tk.Button(root, text="Start Scanning!", command=move_motors)
submit_button.grid(row=r, column=0, columnspan=2)

root.mainloop()

import RPi.GPIO as GPIO
import tkinter as tk
from time import sleep
from picamera2 import Picamera2, Preview
from picamera2.controls import Controls
from PIL import Image, ImageTk
import io

print("Starting...")

# GPIO pin assignments for stepper motor control
DIR_PIN_X = 6   # Direction pin for X-axis
STEP_PIN_X = 13  # Step pin for X-axis
ENDSTOP_PIN_X = 16  # Endstop pin for X-axis
SLP_PIN_X = 2    # Sleep GPIO Pin

DIR_PIN_Y = 19   # Direction pin for Y-axis
STEP_PIN_Y = 26  # Step pin for Y-axis
ENDSTOP_PIN_Y = 16 # 13  # Endstop pin for Y-axis
SLP_PIN_Y = 3    # Sleep GPIO Pin

DIR_PIN_Z = 20    # Direction pin for Z-axis
STEP_PIN_Z = 21  # Step pin for Z-axis
ENDSTOP_PIN_Z = 16 # 5 # Endstop pin for Z-axis
SLP_PIN_Z = 4    # Sleep GPIO Pin

# Stepper motor setup
GPIO.setmode(GPIO.BCM)
GPIO.setup([DIR_PIN_X, STEP_PIN_X, DIR_PIN_Y, STEP_PIN_Y, DIR_PIN_Z, STEP_PIN_Z], GPIO.OUT)
GPIO.setup([ENDSTOP_PIN_X, ENDSTOP_PIN_Y, ENDSTOP_PIN_Z], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to activate motors
def activate_motors(STEP_PIN):
    GPIO.setup([SLP_PIN_X, SLP_PIN_Y, SLP_PIN_Z], GPIO.OUT)
    if STEP_PIN == STEP_PIN_X or STEP_PIN == "all":
        GPIO.output(SLP_PIN_X, GPIO.HIGH)
        print("Activating X")
    if STEP_PIN == STEP_PIN_Y or STEP_PIN == "all":
        GPIO.output(SLP_PIN_Y, GPIO.HIGH)
        print("Activating Y")
    if STEP_PIN == STEP_PIN_Z or STEP_PIN == "all":
        GPIO.output(SLP_PIN_Z, GPIO.HIGH)
        print("Activating Z")
    sleep(0.05)

# Function to deactivate motors
def deactivate_motors(STEP_PIN):        
    global homed_x
    global homed_y
    global homed_z
    
    GPIO.setup([SLP_PIN_X, SLP_PIN_Y, SLP_PIN_Z], GPIO.OUT)

    if STEP_PIN == STEP_PIN_X or STEP_PIN == "all":
        print("Deactivating X")
        GPIO.output(SLP_PIN_X, GPIO.LOW)
        # homed_x = 0
    if STEP_PIN == STEP_PIN_Y or STEP_PIN == "all":
        print("Deactivating Y")
        GPIO.output(SLP_PIN_Y, GPIO.LOW)
        homed_y = 0
    if STEP_PIN == STEP_PIN_Z or STEP_PIN == "all":
        print("Deactivating Z")
        GPIO.output(SLP_PIN_Z, GPIO.LOW)
        homed_z = 0
        


def set_camera():
    global exposure
    global gain
    exposure = 25*1000
    gain = 0
    # ~ exposure = (int(entry_exposure.get())-0) *1000
    # ~ gain = int(entry_gain.get())-0
    print("setting camera to ", exposure, " ", gain)
        
    ctrls = Controls(picam2)
    ctrls.AnalogueGain = gain
    ctrls.ExposureTime = exposure
    picam2.set_controls(ctrls)

    print("waiting for 1 second to apply camera settings...")
    # sleep(1)
    
# Activate all motors on startup
print("Deactivating motors.")
deactivate_motors(STEP_PIN="all")

speed = 0.0005 # 0.001

# ~ # Picamera2 setup
# ~ picam2 = Picamera2()
# ~ camera_config = picam2.create_still_configuration()  # Create the camera configuration
# ~ camera_config["controls"]["FrameRate"] = 30  # Set to desired frame rate
# ~ picam2.configure(camera_config)
# ~ picam2.start()

# ~ Picamera intialisation
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
capture_config = picam2.create_still_configuration()
print("Starting camera and preview...")
# ~ picam2.start_preview(Preview.QTGL)
picam2.configure(preview_config)

picam2.start()
sleep(1)
set_camera()

# homing states
homed_x = 1
homed_y = 0
homed_z = 0

# Current positions of the motors
current_position_x = 0
current_position_y = 0
current_position_z = 0

# Variable that controls motor enable state
enable_motors = 0  # Set to 1 to ensable buttons, 1 to enable

# Define motor control functions
def move_motor(step_pin, dir_pin, steps, direction, speed):
    if step_pin == STEP_PIN_X and homed_x == 0:
            print("X not homed")
            return
    if step_pin == STEP_PIN_Y and homed_y == 0:
            print("Y not homed")
            return
    if step_pin == STEP_PIN_Z and homed_z == 0:
            print("Z not homed")
            return
    activate_motors(STEP_PIN=step_pin)
    """Moves a motor in a given direction for a given number of steps."""
    GPIO.output(dir_pin, direction)
    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        sleep(speed)
        GPIO.output(step_pin, GPIO.LOW)
        sleep(speed)

def check_endstop(endstop_pin):
    """Checks if an endstop has been hit."""
    return GPIO.input(endstop_pin) == GPIO.LOW

def home_axis(step_pin, dir_pin, endstop_pin):
            
    global homed_x
    global homed_y
    global homed_z
    
    global current_position_x
    global current_position_y
    global current_position_z
    
    """Homing procedure for one axis."""
    activate_motors(STEP_PIN=step_pin)
    
    # set direction to move towards endstop per axis
    if dir_pin == DIR_PIN_Y:
            curr_dir = GPIO.HIGH
    if dir_pin == DIR_PIN_Z:
            curr_dir = GPIO.LOW
            
    GPIO.output(dir_pin, curr_dir)  # Move towards endstop
    while check_endstop(endstop_pin):
        GPIO.output(step_pin, GPIO.HIGH)
        sleep(speed)  # Adjust speed as needed
        GPIO.output(step_pin, GPIO.LOW)
        sleep(speed)
    # ~ if endstop_pin == ENDSTOP_PIN_X:
            # ~ homed_x = 1
    print("x homed")
    current_position_x = 0
    if endstop_pin == ENDSTOP_PIN_Y:
            homed_y = 1
            current_position_y = 0
            print("y homed")
    if endstop_pin == ENDSTOP_PIN_Z:
            homed_z = 1
            current_position_z = 0
            print("z homed")

    # Now move a little bit away from the endstop
    sleep(0.5)
    GPIO.output(dir_pin, GPIO.HIGH)  # Move away from endstop
    for _ in range(50):  # Move a small number of steps away
        GPIO.output(step_pin, GPIO.HIGH)
        sleep(speed)
        GPIO.output(step_pin, GPIO.LOW)
        sleep(speed)

def home_all_axes():
    """Homing all axes by running the homing procedure on X, Y, and Z."""
    # ~ home_axis(STEP_PIN_X, DIR_PIN_X, ENDSTOP_PIN_X)
    # ~ sleep(.25)
    home_axis(STEP_PIN_Y, DIR_PIN_Y, ENDSTOP_PIN_Y)
    sleep(.25)
    home_axis(STEP_PIN_Z, DIR_PIN_Z, ENDSTOP_PIN_Z)

# Move motors to absolute positions based on slider values
def move_to_position(step_pin, dir_pin, current_position, target_position, speed):
    # ~ print("moving to position "+str(target_position)+"...")
    step_count = abs(target_position - current_position)
    direction = GPIO.HIGH if target_position > current_position else GPIO.LOW
    move_motor(step_pin, dir_pin, step_count, direction, speed)
    return target_position

# Move motors by a specified step count
def move_by_steps(step_pin, dir_pin, current_position, step_count, direction, speed):
    move_motor(step_pin, dir_pin, step_count, direction, speed)
    return current_position + step_count if direction == GPIO.HIGH else current_position - step_count

    
# GUI setup
class MotorControlApp:
    def __init__(self, root):        
        self.root = root
        self.root.title("PiScAnt Motor Control")
        
        curr_row=0
        
        # Create a frame for the camera preview
        self.preview_frame = tk.Frame(root)
        self.preview_frame.grid(row=0, column=0, padx=5, pady=5)

        # Create camera preview canvas
        self.camera_preview = tk.Label(self.preview_frame)
        self.camera_preview.pack()

        # Create a frame for the control buttons and sliders
        self.control_frame = tk.Frame(root)
        self.control_frame.grid(row=curr_row, column=1, padx=5, pady=5)
        
        curr_row = 0
        # Create buttons to (de)activate motors
        self.x_plus = tk.Button(self.control_frame, text="Deactivate motors", command=lambda: deactivate_motors(STEP_PIN="all"))
        self.x_plus.grid(row=curr_row, column=3)

        self.move_x_minus = tk.Button(self.control_frame, text="Activate motors", command=lambda: activate_motors(STEP_PIN="all"))
        self.move_x_minus.grid(row=curr_row, column=4)
        
        curr_row = curr_row+1
        # Create sliders for X, Y, Z axis
        self.x_slider = tk.Scale(self.control_frame, from_=-1000, to=1000, orient=tk.HORIZONTAL, label="X Axis Steps", command=self.x_slider_moved)
        self.x_slider.grid(row=curr_row+0, column=0, columnspan=2)

        self.y_slider = tk.Scale(self.control_frame, from_=-1000, to=1000, orient=tk.HORIZONTAL, label="Y Axis Steps", command=self.y_slider_moved)
        self.y_slider.grid(row=curr_row+1, column=0, columnspan=2)

        self.z_slider = tk.Scale(self.control_frame, from_=-1000, to=1000, orient=tk.HORIZONTAL, label="Z Axis Steps", command=self.z_slider_moved)
        self.z_slider.grid(row=curr_row+2, column=0, columnspan=2)
        
        # Create input fields for step amounts
        self.x_step_entry = tk.Entry(self.control_frame, width=5)
        self.x_step_entry.insert(0, "90")
        self.x_step_entry.grid(row=curr_row+0, column=2)

        self.y_step_entry = tk.Entry(self.control_frame, width=5)
        self.y_step_entry.insert(0, "90")
        self.y_step_entry.grid(row=curr_row+1, column=2)

        self.z_step_entry = tk.Entry(self.control_frame, width=5)
        self.z_step_entry.insert(0, "90")
        self.z_step_entry.grid(row=curr_row+2, column=2)
        
        # Create buttons to move motors
        self.move_x_plus = tk.Button(self.control_frame, text="Move X Left", command=self.move_x_left)
        self.move_x_plus.grid(row=curr_row, column=3)

        self.move_x_minus = tk.Button(self.control_frame, text="Move X Right", command=self.move_x_right)
        self.move_x_minus.grid(row=curr_row, column=4)
        
        curr_row = curr_row+1
        
        self.move_y_plus = tk.Button(self.control_frame, text="Move Y Left", command=self.move_y_left)
        self.move_y_plus.grid(row=curr_row, column=3)

        self.move_y_minus = tk.Button(self.control_frame, text="Move Y Right", command=self.move_y_right)
        self.move_y_minus.grid(row=curr_row, column=4)

        curr_row = curr_row+1
        
        self.move_z_plus = tk.Button(self.control_frame, text="Move Z Left", command=self.move_z_left)
        self.move_z_plus.grid(row=curr_row, column=3)

        self.move_z_minus = tk.Button(self.control_frame, text="Move Z Right", command=self.move_z_right)
        self.move_z_minus.grid(row=curr_row, column=4)
        
        # Create absolute position buttons for X, Y, Z

        curr_row = curr_row+1
        
        self.move_x_minus_180 = tk.Button(self.control_frame, text="Move X -180", command=self.move_x_to_minus180)
        self.move_x_minus_180.grid(row=curr_row, column=0)

        self.move_x_zero = tk.Button(self.control_frame, text="Move X 0", command=self.move_x_to_zero)
        self.move_x_zero.grid(row=curr_row, column=1)

        self.move_x_plus_180 = tk.Button(self.control_frame, text="Move X +180", command=self.move_x_to_plus180)
        self.move_x_plus_180.grid(row=curr_row, column=2)

        curr_row = curr_row+1

        self.move_y_minus_180 = tk.Button(self.control_frame, text="Move Y -180", command=self.move_y_to_minus180)
        self.move_y_minus_180.grid(row=curr_row, column=0)

        self.move_y_zero = tk.Button(self.control_frame, text="Move Y 0", command=self.move_y_to_zero)
        self.move_y_zero.grid(row=curr_row, column=1)

        self.move_y_plus_180 = tk.Button(self.control_frame, text="Move Y +180", command=self.move_y_to_plus180)
        self.move_y_plus_180.grid(row=curr_row, column=2)

        curr_row = curr_row+1

        self.move_z_minus_180 = tk.Button(self.control_frame, text="Move Z -180", command=self.move_z_to_minus180)
        self.move_z_minus_180.grid(row=curr_row, column=0)

        self.move_z_zero = tk.Button(self.control_frame, text="Move Z 0", command=self.move_z_to_zero)
        self.move_z_zero.grid(row=curr_row, column=1)

        self.move_z_plus_180 = tk.Button(self.control_frame, text="Move Z +180", command=self.move_z_to_plus180)
        self.move_z_plus_180.grid(row=curr_row, column=2)

        # Create focus stacking interval slider

        curr_row = curr_row+1
        
        self.focus_intervals_slider = tk.Scale(self.control_frame, from_=1, to=40, orient=tk.HORIZONTAL, label="Focus stops")
        self.focus_intervals_slider.set(12)  # Set default value to 12
        self.focus_intervals_slider.grid(row=curr_row, column=0, columnspan=2)
        
        # Create buttons for homing and running procedure
        curr_row = curr_row+2
        
        self.home_button = tk.Button(self.control_frame, text="Home All", command=self.home_all_axes)
        self.home_button.grid(row=curr_row, column=0)

        self.run_button = tk.Button(self.control_frame, text="Star Scan!", command=self.run_procedure)
        self.run_button.grid(row=curr_row, column=1)

        # Create alarm indicators for endstops

        curr_row = curr_row+1
        
        self.alarm_x = tk.Label(self.control_frame, text="🚨", font=("Arial", 24), fg="red")
        self.alarm_x.grid(row=curr_row, column=0)

        self.alarm_y = tk.Label(self.control_frame, text="🚨", font=("Arial", 24), fg="red")
        self.alarm_y.grid(row=curr_row, column=1)

        self.alarm_z = tk.Label(self.control_frame, text="🚨", font=("Arial", 24), fg="red")
        self.alarm_z.grid(row=curr_row, column=2)
        
        # Start updating the camera preview
        self.update_camera_preview()
        self.update_alarm_status()

    # Movement methods for each axis
    def move_x_to_minus180(self):
        """Move X motor to -180."""
        # ~ print("Moving X to -180")
        global current_position_x
        current_position_x = move_to_position(STEP_PIN_X, DIR_PIN_X, current_position_x, -180, speed)
        self.x_slider.set(current_position_x)

    def move_x_to_zero(self):
        """Move X motor to 0."""
        global current_position_x
        current_position_x = move_to_position(STEP_PIN_X, DIR_PIN_X, current_position_x, 0, speed)
        self.x_slider.set(current_position_x)

    def move_x_to_plus180(self):
        """Move X motor to +180."""
        global current_position_x
        current_position_x = move_to_position(STEP_PIN_X, DIR_PIN_X, current_position_x, 180, speed)
        self.x_slider.set(current_position_x)

    def move_y_to_minus180(self):
        """Move Y motor to -180."""
        global current_position_y
        current_position_y = move_to_position(STEP_PIN_Y, DIR_PIN_Y, current_position_y, -180, speed)
        self.y_slider.set(current_position_y)

    def move_y_to_zero(self):
        """Move Y motor to 0."""
        global current_position_y
        current_position_y = move_to_position(STEP_PIN_Y, DIR_PIN_Y, current_position_y, 0, speed)
        self.y_slider.set(current_position_y)

    def move_y_to_plus180(self):
        """Move Y motor to +180."""
        global current_position_y
        current_position_y = move_to_position(STEP_PIN_Y, DIR_PIN_Y, current_position_y, 180, speed)
        self.y_slider.set(current_position_y)

    def move_z_to_minus180(self):
        """Move Z motor to -180."""
        global current_position_z
        current_position_z = move_to_position(STEP_PIN_Z, DIR_PIN_Z, current_position_z, -180, speed)
        self.z_slider.set(current_position_z)

    def move_z_to_zero(self):
        """Move Z motor to 0."""
        global current_position_z
        current_position_z = move_to_position(STEP_PIN_Z, DIR_PIN_Z, current_position_z, 0, speed)
        self.z_slider.set(current_position_z)

    def move_z_to_plus180(self):
        """Move Z motor to +180."""
        global current_position_z
        current_position_z = move_to_position(STEP_PIN_Z, DIR_PIN_Z, current_position_z, 180, speed)
        self.z_slider.set(current_position_z)

    def move_x_left(self):
        """Move X motor left by a specified number of steps."""
        global current_position_x
        step_count = int(self.x_step_entry.get())
        current_position_x = move_by_steps(STEP_PIN_X, DIR_PIN_X, current_position_x, step_count, GPIO.LOW, speed)
        self.x_slider.set(current_position_x)

    def move_x_right(self):
        """Move X motor right by a specified number of steps."""
        global current_position_x
        step_count = int(self.x_step_entry.get())
        current_position_x = move_by_steps(STEP_PIN_X, DIR_PIN_X, current_position_x, step_count, GPIO.HIGH, speed)
        self.x_slider.set(current_position_x)

    def move_y_left(self):
        """Move Y motor left by a specified number of steps."""
        global current_position_y
        step_count = int(self.y_step_entry.get())
        current_position_y = move_by_steps(STEP_PIN_Y, DIR_PIN_Y, current_position_y, step_count, GPIO.LOW, speed)
        self.y_slider.set(current_position_y)

    def move_y_right(self):
        """Move Y motor right by a specified number of steps."""
        global current_position_y
        step_count = int(self.y_step_entry.get())
        current_position_y = move_by_steps(STEP_PIN_Y, DIR_PIN_Y, current_position_y, step_count, GPIO.HIGH, speed)
        self.y_slider.set(current_position_y)

    def move_z_left(self):
        """Move Z motor left by a specified number of steps."""
        global current_position_z
        step_count = int(self.z_step_entry.get())
        current_position_z = move_by_steps(STEP_PIN_Z, DIR_PIN_Z, current_position_z, step_count, GPIO.LOW, speed)
        self.z_slider.set(current_position_z)

    def move_z_right(self):
        """Move Z motor right by a specified number of steps."""
        global current_position_z
        step_count = int(self.z_step_entry.get())
        current_position_z = move_by_steps(STEP_PIN_Z, DIR_PIN_Z, current_position_z, step_count, GPIO.HIGH, speed)
        self.z_slider.set(current_position_z)

    def x_slider_moved(self, value):
        """Callback for when the X-axis slider is moved."""
        global current_position_x
        target_position_x = int(value)
        current_position_x = move_to_position(STEP_PIN_X, DIR_PIN_X, current_position_x, target_position_x, speed)

    def y_slider_moved(self, value):
        """Callback for when the Y-axis slider is moved."""
        global current_position_y
        target_position_y = int(value)
        current_position_y = move_to_position(STEP_PIN_Y, DIR_PIN_Y, current_position_y, target_position_y, speed)

    def z_slider_moved(self, value):
        """Callback for when the Z-axis slider is moved."""
        global current_position_z
        target_position_z = int(value)
        current_position_z = move_to_position(STEP_PIN_Z, DIR_PIN_Z, current_position_z, target_position_z, speed)

    def home_all_axes(self):
        """Call the homing procedure for all axes."""
        home_all_axes()

    def run_procedure(self):
        """Start the run procedure with focus stacking."""
        x_steps = self.x_slider.get()
        y_steps = self.y_slider.get()
        z_steps = self.z_slider.get()
        focus_intervals = self.focus_intervals_slider.get()
        run_procedure(x_steps, y_steps, z_steps, focus_intervals, speed)

    # Update camera preview method
    def update_camera_preview(self):
        """Updates the live camera preview in the Tkinter GUI."""
        image = picam2.capture_array()
        image = Image.fromarray(image)
        image = image.resize((round(320*2.5), round(240*2.5)))  # Resize for the preview
        photo = ImageTk.PhotoImage(image)

        self.camera_preview.config(image=photo)
        self.camera_preview.image = photo

        # Update the preview every 33 milliseconds (approx. 30 FPS)
        self.root.after(100, self.update_camera_preview)
    
    # ~ def update_button_state(self):

        # ~ # Repeat the check every 100 ms
        # ~ self.root.after(100, self.update_button_state)
        
    def update_alarm_status(self):
            
        global homed_x
        global homed_y
        global homed_z

        """Updates the alarm status based on endstop triggers."""
        if check_endstop(ENDSTOP_PIN_X):
            self.alarm_x.config(fg="green")  # Change to green if endstop is pressed
        else:
            self.alarm_x.config(fg="red")  # Change to red if endstop is not pressed

        if check_endstop(ENDSTOP_PIN_Y):
            self.alarm_y.config(fg="green")
        else:
            self.alarm_y.config(fg="red")

        if check_endstop(ENDSTOP_PIN_Z):
            self.alarm_z.config(fg="green")
        else:
            self.alarm_z.config(fg="red")
        
        
        # ~ print(homed_x)
        if homed_x == 0:
                self.alarm_x.config(bg="darkorange")  # Change to darkorange if not homed
                self.move_x_plus.config(state="disabled") # deactivate mótor movement button
                self.move_x_minus.config(state="disabled") # deactivate mótor movement button
                self.move_x_minus_180.config(state="disabled") # deactivate mótor movement button
                self.move_x_zero.config(state="disabled") # deactivate mótor movement button
                self.move_x_plus_180.config(state="disabled") # deactivate mótor movement button
                self.run_button.config(state="disabled") # deactivate Start Scan! button
        else:
                self.alarm_x.config(bg="green")  # Change to green if homed
                self.move_x_plus.config(state="normal") # activate mótor movement button
                self.move_x_minus.config(state="normal") # activate mótor movement button
                self.move_x_minus_180.config(state="normal") # activate mótor movement button
                self.move_x_zero.config(state="normal") # activate mótor movement button
                self.move_x_plus_180.config(state="normal") # activate mótor movement button
                
        if homed_y == 0:
                self.alarm_y.config(bg="darkorange")  # Change to darkorange if not homed
                self.move_y_plus.config(state="disabled") # deactivate mótor movement button
                self.move_y_minus.config(state="disabled") # deactivate mótor movement button
                self.move_y_minus_180.config(state="disabled") # deactivate mótor movement button
                self.move_y_zero.config(state="disabled") # deactivate mótor movement button
                self.move_y_plus_180.config(state="disabled") # deactivate mótor movement button
                self.run_button.config(state="disabled") # deactivate Start Scan! button
        else:
                self.alarm_y.config(bg="green")  # Change to green if homed
                self.move_y_plus.config(state="normal") # activate mótor movement button
                self.move_y_minus.config(state="normal") # activate mótor movement button
                self.move_y_minus_180.config(state="normal") # activate mótor movement button
                self.move_y_zero.config(state="normal") # activate mótor movement button
                self.move_y_plus_180.config(state="normal") # activate mótor movement button
                
        if homed_z == 0:
                self.alarm_z.config(bg="darkorange")  # Change to darkorange if not homed
                self.move_z_plus.config(state="disabled") # deactivate mótor movement button
                self.move_z_minus.config(state="disabled") # deactivate mótor movement button
                self.move_z_minus_180.config(state="disabled") # deactivate mótor movement button
                self.move_z_zero.config(state="disabled") # deactivate mótor movement button
                self.move_z_plus_180.config(state="disabled") # deactivate mótor movement button
                self.run_button.config(state="disabled") # deactivate Start Scan! button
        else:
                self.alarm_z.config(bg="green")  # Change to green if homed
                self.move_z_plus.config(state="normal") # activate mótor movement button
                self.move_z_minus.config(state="normal") # activate mótor movement button
                self.move_z_minus_180.config(state="normal") # activate mótor movement button
                self.move_z_zero.config(state="normal") # activate mótor movement button
                self.move_z_plus_180.config(state="normal") # activate mótor movement button
        
        if homed_x != 0 and homed_y != 0 and homed_z != 0:
                        self.run_button.config(state="normal") # activate Start Scan! button
        # ~ global enable_motors
        # ~ """Enable or disable motor movement buttons based on `enable_motors`."""
        # ~ if enable_motors == 0:
                # ~ "disabled"
        # ~ self.y_left_button.config(state=state)
        # ~ self.y_right_button.config(state=state)
        # ~ self.z_left_button.config(state=state)
        # ~ self.z_right_button.config(state=state)
        
        self.x_slider.set(current_position_x)
        self.y_slider.set(current_position_y)
        self.z_slider.set(current_position_z)
        
        # Repeat the alarm status check every 100ms
        self.root.after(100, self.update_alarm_status)

# Initialize the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = MotorControlApp(root)
    root.mainloop()

    # Cleanup GPIO and stop camera on exit
    GPIO.cleanup()
    picam2.stop()

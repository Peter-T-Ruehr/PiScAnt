from time import sleep
from picamerax import PiCamera
import os
import subprocess
import tkinter as tk 
from tkinter import messagebox

camera = PiCamera()
camera.resolution = (320, 240)# (4056, 3040) # (1024, 768)
camera.start_preview()
preview = camera.start_preview()
preview.fullscreen = False
preview.window = (800, 5, 320, 240)


# Uses ticcmd to send and receive data from the Tic over USB.
# Works with either Python 2 or Python 3.
#
# NOTE: The Tic's control mode must be "Serial / I2C / USB".


x_axis_stop_dir = 'rev'
z_axis_stop_dir = 'fwd'

position_x = 0
position_y = 0
position_z = 0

def get_motor_ID(axis):
    x_axis_ID = '00363443' # arm
    y_axis_ID = '00338490' # specimen turntable
    z_axis_ID = '00374283' # focus rail
    
    if axis == 'x':
        curr_axis_ID = x_axis_ID
    if axis == 'y':
        curr_axis_ID = y_axis_ID
    if axis == 'z':
        curr_axis_ID = z_axis_ID
        
    return(curr_axis_ID)
    
def get_motor_pos(axis):
    motor_ID = get_motor_ID(axis)
    cmd = 'ticcmd -s -d ' + motor_ID + ' --full'
    test = subprocess.check_output(cmd, shell=True)

    test_string = test.decode()
    index_1 = test_string.index("Current position:")
    index_2 = test_string.index("Position uncertain:")
    motor_pos = int(test_string[(index_1 + 17):(index_2 - 1)].strip(" "))# sleep shortly to read correct number
    # print('Current position of ' + axis + '-axis: ' + str(motor_pos) + '.')
    return(motor_pos)

def move_motor_by_steps(axis, by_steps):
    curr_axis_ID = get_motor_ID(axis)
    
    position_y = get_motor_pos(axis)
    print(axis + '-axis now at ' + str(position_y))
    
    target = position_y + by_steps
    
    print('moving ' + axis + '-axis by ' + str(by_steps) + '...')
    
    cmd = 'ticcmd --exit-safe-start -d ' + curr_axis_ID + ' --position ' + str(target)
    os.system(cmd)
    
    # sleep shortly to read correct number
    sleep(0.25)
    print(axis + '-axis now at ' + str(get_motor_pos(axis)))

def energize():
    cmd = 'ticcmd -d 00363443 --energize'
    os.system(cmd)
    cmd = 'ticcmd -d 00338490 --energize'
    os.system(cmd)
    cmd = 'ticcmd -d 00374283 --energize'
    os.system(cmd)
    
    move_motor_to('x', get_motor_pos('x')+1)
    move_motor_to('y', get_motor_pos('y')+1)
    move_motor_to('z', get_motor_pos('z')+1)
    
def deenergize():
    cmd = 'ticcmd -d 00363443 --deenergize'
    os.system(cmd)
    cmd = 'ticcmd -d 00338490 --deenergize'
    os.system(cmd)
    cmd = 'ticcmd -d 00374283 --deenergize'
    os.system(cmd)
       
def move_motor_to(axis, target):
    curr_axis_ID = get_motor_ID(axis)
        
    position_y = get_motor_pos(axis)
    print(axis + '-axis now at ' + str(position_y))
    
    by_steps = target - position_y
    
    
    print('moving ' + axis + '-axis by ' + str(by_steps) + ' to ' + str(target) + '...')
    
    cmd = 'ticcmd --exit-safe-start -d ' + curr_axis_ID + ' --position ' + str(target)
    os.system(cmd)
    
    # sleep shortly to read correct number
    sleep(0.25)
    get_motor_ID(axis)
    # print(axis + '-axis now at ' + str(get_motor_pos(curr_axis_ID)))

def start_scan(): 
    camera.stop_preview()
    camera.close()
    
    steps_x = 10
    steps_y = 500
    steps_z = 500
    
    y_pos_init = get_motor_pos('y')
    z_pos_init = get_motor_pos('z')
    
    # energize()
    for x in range(2):
        for y in range(2):
            for z in range(2):
                x_pos = get_motor_pos('x')
                y_pos = get_motor_pos('y')
                z_pos = get_motor_pos('z')
                cmd = 'raspistill -t 1 -o ./img_01/x_' + str(x_pos) + '_y_' + str(y_pos) + '_z_' + str(z_pos)  + '.jpg -n -ISO 100, -sh 0, -co 0, -br 50, -sa 0'
                os.system(cmd)
              
                move_motor_by_steps('z', steps_z)  
                
                if(z == max(range(2))):
                    x_pos = get_motor_pos('x')
                    y_pos = get_motor_pos('y')
                    z_pos = get_motor_pos('z')
                    cmd = 'raspistill -t 1 -o ./img_01/x_' + str(x_pos) + '_y_' + str(y_pos) + '_z_' + str(z_pos)  + '.jpg -n -ISO 100, -sh 0, -co 0, -br 50, -sa 0'
                    os.system(cmd)
                    
                    move_motor_to('z', z_pos_init) 
            
            move_motor_by_steps('y', steps_y)
            if(y == max(range(2))):                
                move_motor_to('y', y_pos_init)
        move_motor_by_steps('x', steps_x)
        if(x == max(range(2))):
            for y in range(2):
                for z in range(2):
                    x_pos = get_motor_pos('x')
                    y_pos = get_motor_pos('y')
                    z_pos = get_motor_pos('z')
                    cmd = 'raspistill -t 1 -o ./img_01/x_' + str(x_pos) + '_y_' + str(y_pos) + '_z_' + str(z_pos)  + '.jpg -n -ISO 100, -sh 0, -co 0, -br 50, -sa 0'
                    os.system(cmd)
                  
                    move_motor_by_steps('z', steps_z)  
                    
                    if(z == max(range(2))):
                        x_pos = get_motor_pos('x')
                        y_pos = get_motor_pos('y')
                        z_pos = get_motor_pos('z')
                        cmd = 'raspistill -t 1 -o ./img_01/x_' + str(x_pos) + '_y_' + str(y_pos) + '_z_' + str(z_pos)  + '.jpg -n -ISO 100, -sh 0, -co 0, -br 50, -sa 0'
                        os.system(cmd)
                        
                        move_motor_to('z', z_pos_init) 
                
                move_motor_by_steps('y', steps_y)
# GUI
root = tk.Tk() 
root.title("piscAnt v.0.0.9000")         
# Fixing the window size. 
root.minsize(width=350, height=70) 
label = tk.Label(root, text="piscAnt", fg="black", font="Verdana 14 bold") 
#label.pack()

energize_b = tk.Button(root,
    text='Energize',
    bg='green',
    width=20,
    state='normal',
    command=lambda: energize())

deenergize_b = tk.Button(root,
    text='De-Energize',
    bg='red',
    width=20,
    state='normal',
    command=lambda: deenergize())

lable_turntable = tk.Label(
    root,
    text='specimen turntable', 
)
lable_arm = tk.Label(
    root,
    text='specimen arm', 
)

lable_focus = tk.Label(
    root,
    text='specimen focus', 
)

left_sm = tk.Button(root, text='<< turntable left',  
width=15, state='normal', command=lambda: move_motor_by_steps('y', -100))

right_sm = tk.Button(root, text='turntable right >>',  
width=15, state='normal', command=lambda: move_motor_by_steps('y', +100))

left_big = tk.Button(root, text='<< turntable left',  
width=15, state='normal', command=lambda: move_motor_by_steps('y', -500))

right_big = tk.Button(root, text='turntable right >>',  
width=15, state='normal', command=lambda: move_motor_by_steps('y', +500))

arm_left_sm = tk.Button(root, text='<< arm further',  
width=15, state='normal', command=lambda: move_motor_by_steps('x', +10))

arm_right_sm = tk.Button(root, text='arm closer >>',  
width=15, state='normal', command=lambda: move_motor_by_steps('x', -10))

arm_left_big = tk.Button(root, text='<< arm further',  
width=15, state='normal', command=lambda: move_motor_by_steps('x', +50))

arm_right_big = tk.Button(root, text='arm closer >>',  
width=15, state='normal', command=lambda: move_motor_by_steps('x', -50))

focus_left_sm = tk.Button(root, text='<< focus closer',  
width=15, state='normal', command=lambda: move_motor_by_steps('z', +100))

focus_right_sm = tk.Button(root, text='focus further >>',  
width=15, state='normal', command=lambda: move_motor_by_steps('z', -100))

focus_left_big = tk.Button(root, text='<< focus closer',  
width=15, state='normal', command=lambda: move_motor_by_steps('z', +500))

focus_right_big = tk.Button(root, text='focus further >>',  
width=15, state='normal', command=lambda: move_motor_by_steps('z', -500))

start_scan_b = tk.Button(root, text='Start Scan!',  
width=15, state='normal', command=lambda: start_scan())
# end = tk.Button(root, text='Exit', 
# width=8, state='normal', command=ExitApplication)

r=0
energize_b.grid(row=r,column=0)
deenergize_b.grid(row=r,column=1)
r+=2
lable_turntable.grid(row=r, column=0, columnspan = 2)
r+=1
left_sm.grid(row=r,column=0) 
right_sm.grid(row=r,column=1)
r+=1
left_big.grid(row=r,column=0) 
right_big.grid(row=r,column=1)
r+=1
lable_arm.grid(row=r, column=0, columnspan = 2)
r+=1
arm_left_sm.grid(row=r,column=0) 
arm_right_sm.grid(row=r,column=1)
r+=1
arm_left_big.grid(row=r,column=0) 
arm_right_big.grid(row=r,column=1)
r+=1
lable_focus.grid(row=r, column=0, columnspan = 2)
r+=1
focus_left_sm.grid(row=r,column=0) 
focus_right_sm.grid(row=r,column=1)
r+=1
focus_left_big.grid(row=r,column=0) 
focus_right_big.grid(row=r,column=1)
r+=1
start_scan_b.grid(row=r,column=0, columnspan = 2) 
# end.grid(row=r,column=1)


# fan_off['state']='disabled'
# pump_off['state']='disabled'
root.mainloop()

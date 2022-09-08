# PiscAnt (Pi scAnt)
Python code to run scAnt setup on Raspberry Pi Model 3+. This was developed for my own use, so the code comes with limited documentation. 

Feel free to use this code and its [Discussions](https://github.com/Peter-T-Ruehr/PiscAnt/discussions) and [Issues](https://github.com/Peter-T-Ruehr/PiscAnt/issues) pages.

CAD files to house the RPi HQ cam on the original [scAnt](https://www.thingiverse.com/thing:4694713) or [modified](https://www.thingiverse.com/thing:5479056) scAnt are available on [Thingiverse](https://www.thingiverse.com/thing:5502528).

A model of a praying mantis head generated from the photos taken with this code and setup is available [here](https://skfb.ly/ourV8).

The scAnt author`s original code and documentation are available [here](https://github.com/evo-biomech/scAnt), CAD files [here](https://www.thingiverse.com/thing:4694713), and the related publication [here](https://peerj.com/articles/11155/).

# Installation
## Raspbian
Install Raspbian GNU/Linux 11 (bullseye)

## Enable legacy camera
`sudo raspi-config`
  * Interface Options
  * Legacy Camera: Enable
  * reboot
  
## add imx477 support
`sudo nano /boot/config.txt`

add

`# Enable pi HQ camera`

`dtoverlay=imx477`

out-comment
`# dtoverlay=vc4-fkms-v3d`

See below for some test commands to see if camera works.

## download and install pololu tic 500 drivers
source: https://www.pololu.com/docs/0J71/all#1.2

`cd ~/Downloads`

`tar -xvf pololu-tic-*.tar.xz`

`sudo pololu-tic-*/install.sh`

(re-)plug tics

## check if tics are detectable
`ticcmd --list`

when 3 tics are connected, it should look like this (with your own tic driver numbers):

`0036xxx3,         Tic T500 Stepper Motor Controller`

`0033xxx0,         Tic T500 Stepper Motor Controller`

`0037xxx3,         Tic T500 Stepper Motor Controller`

## start Tic Control Center
`ticgui`

## install picamerax python package
`pip install picamerax`

## some random camera control commands to test camera and find good settings
With help from
https://www.arducam.com/docs/cameras-for-raspberry-pi/native-raspberry-pi-cameras/native-camera-commands-raspistillraspivid/

`raspistill -t 1 -o image.jpg -p100,100,300,200`

`raspistill -t 1 -o image.jpg -n`

`raspistill -t 0 -k -o image.jpg -p 0,0,800,600`

`raspistill -t 0 -k -o image.jpg -p 30,30,800,600 --ISO 200 --shutter 3000 -sh 0 -co 0 -br 50 -sa 0`

`raspistill -t 0 -k -o image.jpg -p 30,30,800,600 --ISO 200 --shutter 3000 -sh 0 -co 0 -br 50 -sa 0 -awb off -awbg 2.9,1.5`

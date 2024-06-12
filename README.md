# SentryTurret
## Overview
This is an autonomous sentry turret piloted by computer vision and controlled by a Raspberry Pi 4 running OpenCV.

## Tech Stack
- Software: Rust, OpenCV, YOLOv3, RPPAL
- Hardware: Raspberry Pi 4, 2 Servo motors, Camera, Gel Blaster
- Chasis: Autodesk Inventor, 3D Printing

## How to Setup Raspberry Pi 4
1. ```sudo apt-get install git``` to install git
2. ```sudo apt-get install libopencv-dev clang libclang-dev``` to install OpenCV dependencies
3. ```curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh``` to install Rust
4. ```echo "dtoverlay=pwm-2chan" | sudo tee -a /boot/firmware/config.txt``` and ```sudo reboot``` to allow hardware pwm access for servos
5. ```git clone https://github.com/emilsharkov/SentryTurret.git``` to clone the repository locally
6. ```cd SentryTurret``` and ```cargo build``` to build project
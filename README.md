# Pie-Cam

## Project-Background

PieCam is a home security surveillance system built on a Raspberry Pi using a Pi-Camera. This system will be user-configurable through the systems’ web interface, it should primarily be used as an outdoor camera and will be connected to the users’ network to ensure
security. Users will receive an email notification when the camera detects movement around
their home.

## The Pie-Cam Team



## Using The Pie-Cam


## Installation (Current)

From a fresh install of Debian
- login (pi, raspberry)
- sudo raspi-config
    - Interface > enable camera module
    - Network > Wifi > Set up wifi
    - (Restart)
- sudo apt update
- sudo apt upgrade
- sudo apt install git
- git clone https://gitlab.socs.uoguelph.ca/macleodl/w20-cis4250.git
- sudo make install



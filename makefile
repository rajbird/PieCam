
install:
	apt -y install python3
	apt -y install python3-opencv
	apt -y install python3-pip
	apt -y install libatlas-base-dev
	apt -y install libjasper-dev
	apt -y install libqtgui4
	apt -y install libgstreamer1.0-0
	apt -y install libqt4-test
	apt -y install python3-pyqt5
	apt -y install cmake
	apt -y install build-essential 
	apt -y install pkg-config 
	apt -y install libgtk2.0-dev 
	apt -y install libtbb-dev 
	apt -y install python-dev 
	apt -y install python-numpy 
	apt -y install python-scipy 
	apt -y install libjpeg-dev 
	apt -y install libpng-dev 
	apt -y install libtiff-dev 
	apt -y install libavcodec-dev 
	apt -y install libavutil-dev 
	apt -y install libavformat-dev 
	apt -y install libswscale-dev 
	apt -y install libdc1394-22-dev 
	apt -y install libv4l-dev
	pip3 install opencv-contrib-python==3.4.3.18
	pip3 install imutils
	pip3 install picamera
	pip3 install flask
	pip3 install psutil
	pip3 install opencv-python
	pip3 install pillow

test:
	python3 test.py
	
run_dev:
	python3 main.py --ip localhost

run_prod:
	LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3 main.py --ip localhost

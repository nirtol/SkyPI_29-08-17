import os

os.system("cd /home/pi/Desktop/Server_new")
os.system("sudo pigpiod")
os.system("python3 app.py")
os.system("cd /home/pi/RPi_Cam_Web_Interface")
os.system("./start.sh")
sudo pip3 install imutils
pip3 install pyzbar (for QR code decoder)
pip3 install xlrd (for excel reading)
sudo apt install mariadb-server (for mySQL)

For OpenCV on Rpi 3
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-100
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
sudo pip3 install opencv-contrib-python==4.1.0.25

For Screenapp
sudo su;
wget -O - https://raw.githubusercontent.com/audstanley/NodeJs-Raspberry-Pi/master/Install-Node.sh | bash;
exit;
node -v;
npm install react-scripts --save

Not needed
sudo apt install fswebcam (using pygame instead)
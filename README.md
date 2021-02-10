# pi_watch
A project to make a pi small enough to wear on your wrist as a watch

font:
https://fonts2u.com/nasalizationrg-regular.font

only if want to run w/o sudo
sudo adduser mikey gpio
sudo adduser mikey dialout
sudo adduser mikey i2c

enable i2c and spi
https://github.com/PiSupply/PaPiRus

Also, install requirements to sudo. 
sudo pip3 install -r requirements.txt

for crontab
sudo python3 /home/mikey/Documents/pi_watch/scripts/auto_watch.py your511apikey

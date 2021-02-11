# pi_watch
A project to make a pi small enough to wear on your wrist as a watch. It can check buses near my apartment, show the weather, and turn off with button presses.    
![pi_watch.gif](./pi_watch.gif)    

I bought a watch case for the pi [here](https://uk.pi-supply.com/products/papirus-zero-case) and an e-ink display from papirus [here](https://uk.pi-supply.com/products/papirus-zero-epaper-screen-phat-pi-zero?_pos=5&_sid=d0eb9502c&_ss=r). The e-ink display has 5 buttons on it which is quite handy!    

## Setup Steps
To set this up, you'll need to set the pi up. I wrote a guide on that you can find [here](https://github.com/MZandtheRaspberryPi/pi_headless_setup). You'll then need to solder some headers to the pi zero and put the e-ink display on top of it.

Then, you'll need to download a font to your home directory on the pi, or make peace with the default font. I like https://fonts2u.com/nasalizationrg-regular.font.    

If your username is jack, and you want to run the watch script without sudo permission, you'll need to add jack to some user groups:
```
sudo adduser jack gpio
sudo adduser jack dialout
sudo adduser jack i2c
```    

You'll need to enable i2c and spi communication in raspi-config interface options
```
sudo raspi-config
```     

You'll also need to follow the instructions on PaPiRus's github to install their API. Find it here: https://github.com/PiSupply/PaPiRus    

Also, install requirements to sudo. 
sudo pip3 install -r requirements.txt

for crontab
sudo python3 /home/mikey/Documents/pi_watch/scripts/auto_watch.py your511apikey

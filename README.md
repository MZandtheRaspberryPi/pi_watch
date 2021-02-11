# pi_watch
A project to make a pi small enough to wear on your wrist as a watch. It can check buses near my apartment, show the weather, and turn off with button presses.    
![pi_watch.gif](./pi_watch.gif)    

I bought a watch case for the pi [here](https://uk.pi-supply.com/products/papirus-zero-case) and an e-ink display from papirus [here](https://uk.pi-supply.com/products/papirus-zero-epaper-screen-phat-pi-zero?_pos=5&_sid=d0eb9502c&_ss=r). The e-ink display has 5 buttons on it which is quite handy!    

## Setup Steps
To set this up, you'll need to set the pi up. I wrote a guide on that you can find [here](https://github.com/MZandtheRaspberryPi/pi_headless_setup). You'll then need to solder some headers to the pi zero and put the e-ink display on top of it.

Then, you'll need to download a font to your home directory on the pi, or make peace with the default font. I like https://fonts2u.com/nasalizationrg-regular.font.    

From here you can clone this repo, then edit the scripts/auto_watch.py file to put the path to your font in the font_path variable.    

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

You'll need to install the libraries I used to make the transit checker and weather checker, to whatever user you run want to run the command as. I run as sudo, so I install for sudo.
```
sudo pip3 install -r requirements.txt
```    

From here you can edit your sudo crontab (if you're running command as sudo) and add a command on reboot to startup the script. If you don't want to call the 511 bay area api to check buses, then you can put in your511apikey instead of a real api key.    
```
sudo crontab -e
```    
add this to the bottom:
```
@reboot sudo python3 /home/jack/pi_watch/scripts/auto_watch.py your511apikey
```     

## Notes on the Scripts
I used 511 SF Bay’s Portal for Open Transit Data to get the buses in my hometown of San Francisco. You can find info on that API and how to create a token [here](https://511.org/open-data/transit). In the get_transit.py code I document some useful links to resources for finding stop ids and navigating the datastructure.    

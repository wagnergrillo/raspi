#! /bin/sh
rm -rf LCD-show
git clone https://github.com/Lcdwiki/LCD-show
chmod -R 755 LCD-show
sudo mkdir /home/pi/.config/autostart
sudo cp auto.desktop /home/pi/.config/autostart/auto.desktop
sudo cp autostart /etc/xdg/lxsession/LXDE-pi/autostart
sudo cp lightdm.conf /etc/lightdm
cd LCD-show
./MHS35-show

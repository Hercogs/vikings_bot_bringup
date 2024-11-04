#!/bin/bash

echo "deleting rules for joystick"
echo "sudo rm   /etc/udev/rules.d/99-joystick.rules"
sudo rm   /etc/udev/rules.d/99-joystick.rules
echo " "
echo "Restarting udev"
echo ""
sudo service udev reload
sudo service udev restart
echo "finish  delete"
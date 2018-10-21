sudo fxload -t fx2 -D /dev/bus/usb/002/002 -I  hp-gpib/gpib_firmware-2008-08-10/agilent_82357a/measat_releaseX1.8.hex
sleep 3
sudo fxload -t fx2 -D /dev/bus/usb/002/003 -I  hp-gpib/gpib_firmware-2008-08-10/agilent_82357a/measat_releaseX1.8.hex
sudo gpib_config
sleep 2
sudo chgrp gpib /dev/gpib*
sudo chmod 660 /dev/gpib*

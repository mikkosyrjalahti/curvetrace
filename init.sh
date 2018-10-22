#!/bin/bash

fxload -t fx2 -D /dev/bus/usb/002/002 -I  fw/agilent_82357a/measat_releaseX1.8.hex
sleep 3

fxload -t fx2 -D /dev/bus/usb/002/003 -I  fw/agilent_82357a/measat_releaseX1.8.hex

gpib_config
sleep 2

chgrp gpib /dev/gpib*
chmod 660 /dev/gpib*

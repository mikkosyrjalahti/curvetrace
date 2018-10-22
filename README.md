h1 HP 4142B Modular DC Source/Monitor as curve tracer

This is my playground for doing some curve tracing with an older HP SMU on Linux with Jupyter Python notebooks.

If you don't like something, you're free to change whatever (and submit/form your changes if
you feel they could be useful to someone else).

h2 Hardware setup

My unit has GNDU, 3 41420A SMU units and 41425A AFU, which is used for some measurements.
You'll need to edit relevant parts to suit your setup.

For GBIP I'm using Agilent 82357b

h2 Using

Install Linux GPIB support https://linux-gpib.sourceforge.io/

Run init.sh as root (It's likely that you need to edit the USB paths - firmware is loaded 2 times and the USB is reconnected with different path each time when the dongle boots.

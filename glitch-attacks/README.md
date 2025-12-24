# Glitch-attack

Scripts for injecting glitch attacks for the Raspberry Pi 3b v2 and Raspberry Pi 4b

## glitch-ssh*.ipynb

These files are used for glitch attacks that automatically detect if the target has made a logic mistake. They work by opening an SSH connection to the target, running the program over SSH, then injecting the glitch, and observing the output to see if it matches expectations. The specific files may contain variations, such as setups to reboot the target if it freezes and faster glitch repeat incrementation systems. 

The `glitch-ssh-long-glitch.ipynb` variation injects a very long glitch by using multiple glitches in a row. 

The `glitch-ssh-io.ipynb` variation injects a glitch into a program that performs I/O operations. 

## glitch-manual.ipynb

These files are used for manual glitches by continously mounting glitch attacks. After a glitch has been injected, the user must observe the target manually. The target program may be run manually or it may contain an infinite loop. 

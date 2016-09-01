## Overview 
Bravia Console is a simple console interface written in Python to send remote control commands to a Sony Bravia TV.

The reason behind this project was that I wanted to watch a 3D movie via the Plex Android TV app which did not support enabling 3D. After a bit of googling, I identified a workaround for this by sending the remote control commands via HTTP via a shell script. I also found other projects doing the same in slightly different ways. Nothing worked out of the box for me or at least not how I wanted it to work.  Nothing in this project is groundbreaking or new, I just wanted to a) learn a bit more how this all worked and b) to implement something that worked straight up how I wanted.

When the app is run, it will search the local network for a Bravia TV via a SSDP request. When a TV is found it will query it for its system information and then another query for all the remote control commands that it supports. When this is done, you can simply enter the command in the console to send it to the TV.

Projects on which I copied/borrowed implementation ideas from:  
https://github.com/breunigs/bravia-auth-and-remote  
https://github.com/aparraga/braviarc  
https://github.com/bunk3r/braviapy 

Note: This has been tested on Windows 10 (Python 2.7 and 3.5) and on Debian (Python 2.7) with a Sony Bravia TV (Model KDL-55W800C).

## Set Up 
This project relies on using a shared key which is setup manually on the TV one time.

Instructions to setup PSK (Pre-Shared Key) on TV:  
1. Navigate to: [Settings] -> [Network] -> [Home Network Setup] -> [IP Control]  
2. Set [Authentication] to [Normal and Pre-Shared Key]  
3. There should be a new menu entry [Pre-Shared Key]. Set it to '000'  
Note: To modify the PSK in this console enter 'set option psk <value>' 

## Usage

`python bravia_console.py`

![Banner](https://raw.githubusercontent.com/darkosancanin/bravia_console/master/screenshots/banner.png)

![Help](https://raw.githubusercontent.com/darkosancanin/bravia_console/master/screenshots/help.png)

![Search](https://raw.githubusercontent.com/darkosancanin/bravia_console/master/screenshots/search.png)

![Sending Commands](https://raw.githubusercontent.com/darkosancanin/bravia_console/master/screenshots/sending_command.png)

![Show Commands](https://raw.githubusercontent.com/darkosancanin/bravia_console/master/screenshots/show_commands.png)

![Show Info](https://raw.githubusercontent.com/darkosancanin/bravia_console/master/screenshots/show_info.png)


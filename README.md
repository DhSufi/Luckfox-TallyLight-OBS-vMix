# Luckfox-TallyLight-OBS-vMix
Simple client that runs on Luckfox Pico Pro (or similar development boards). It can be configured to connect to OBS Studio Websocket or Vmix TCP API. Then powers on/off the led of the board on configuration demand.

![Example setup](https://raw.githubusercontent.com/DhSufi/Luckfox-TallyLight-OBS-vMix/main/TallyLuckfox.png)

The main goal of the script is to have full control of the setup via LAN network. Some cameras (like Blackmagic) may have built-in Tally lights but they can only be controlled via BNC inputs (they do not allow REST API for Tally control). Also other cameras do not even have built-in tally lights.  

So instead of laying tons of expensive coaxial cable with weird changing connectors between cameras (like Micro-BNC, Mini-BNC or BNC) you can just lay a single ethernet cable and control not only your own tally but also the cameras with their REST API (ISO, Shutter Speed, etc.)  

For my personal use, the idea is to lay just a single POE ethernet cable for each tripod. Then depending on the camera, if I only need to control Tally, I use a simple POE splitter to transfer data and power to the Luckfox Pico Pro. On the other hand if there is also need of controlling the camera (PTZ/REST API), I use a tiny POE powered switch ethernet with 3 ports. This will transfer data to the Camera and the Luckfox. And for powering the luckfox I use the USB camera port. There are many ways to build your setup. I would appreciate it if you could comment yours in this repo issues.

## Script features

During runtime, the script will detect if the *tally.conf* file was edited and reload the configuration and start working again with the new parameters. This means you dont need to restart the board each time you change the configuration.  

During runtime, if OBS Studio/vMix are closed or connection is lost, the script will reconnect automatically to OBS Studio/vMix and work again. This means you do not need to restart the board each time connection is lost.

On other hand, it is high recommended to make the script runs on start up, so if power is lost you do not need to run manually the script. You can follow any tutorial about that regard.
Here is my personal example, but please note it may not be applicable to your personal set up:

`sudo nano /etc/rc.local`

Then add the following line to the end of the file and save it:

`sudo bash -c 'python /home/user/Tally.py > /home/user/my.log 2>&1' &`






## Edit the script to match your setup
Change in the script the path and pins of your setup (# CHANGE TO YOUR NEEDS)

## Usage
Edit file called **tally.conf**  
In this file you must set up the following parameters:

Example for OBS SOURCE:

`software: "obs"`  
`ip: "localhost"`  
`port: "4455"`  
`source: "Caster Cam"`  

Example for OBS SCENE:

`software: "obs"`  
`ip: "localhost"`  
`port: "4455"`  
`scene: "Main Stage"`  

Example for vMix:  

`software: "vmix"`  
`ip: "localhost"`  
`port: "8099"`  
`input: "3"` 

When using OBS SOURCE it is important to respect spaces inside the quotes, as long as OBS consider them different sources. For example:

`source: "Caster Cam"`

it is diferent from:

`source: "Caster Cam "`

or different from:

`source: "CasterCam"`

Be careful with that.


When using vMix it only triggers input NUMBER. That means, if you close an input, then the order may change and the input number X is a diferrent resource. Be careful with that.


This script uses:

https://github.com/IRLToolkit/simpleobsws  

https://github.com/vsergeev/python-periphery





# Luckfox-TallyLight-OBS-vMix
Simple client that runs on Luckfox Pico Pro (or similar development boards). It can be configured to connect to OBS Studio Websocket or Vmix TCP API. Then powers on/off the led of the board on configuration demand


Change in the script the path and pins of your setup (# CHANGE TO YOUR NEEDS)

The script reads the file called tally.conf. In this file you must set up the following parameters:

  Example for OBS SOURCE:
   
  `software: "obs"
  ip: "localhost"
  port: "4455"
  source: "Caster Cam"`
  
  Example for OBS SCENE:
  
  `>software: "obs"
  >ip: "localhost"
  >port: "4455"
  >scene: "Main Stage"
  `

  Example for vMix:
  
  `>software: "vmix"
  >ip: "192.168.1.132"
  >port: "8099"
  >input: "3"
  `

When using OBS SOURCE it is important to respect spaces inside the quotes, as long as OBS consider them different sources. For example:

source: "Caster Cam"

it is diferent from:

source: "Caster Cam "

or different from:

source: "CasterCam"

Be careful with that.


When using vMix it only triggers input NUMBER. That means, if you close an input, then the order may change and the input number 3 is a diferrent resource. Be careful with that.



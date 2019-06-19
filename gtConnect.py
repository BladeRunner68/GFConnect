#!/usr/bin/env python
########################
#program name: gfConnect.py
#Author: S Taylor
#Date: 15-Jun-19
#Purpose: Proof of concept for connecting and controlling the Grainfather Connect Boiler Controller from my RPI (2 - with bluetooth dongle & 3) 
#Version: 0.1
#Requires:  RPI (or Linux host!), Bluez, Bluepy (Python moodule), Python 2.7
########################
#Caller info: python gfConnect.py <GF Controller BLE Address> <command>
#<GF Controller address> = ble address for GF Controller
#<command> = enclosed command (including trailing commas where necessary) for activating functions on GF controller.
#Example run command: python gfConnect.py BB:A0:50:12:09:1G '$70,'
#########################
#command list so far:
#timer: Sx where x = mins to set - example: S1 for 1 minute timer, S5 for five minute timer.
#cancel: C0
#pause or resume: G
#temp up: U
#temp down: D
#heat toggle: H
#pump toggle: P
#temp set point: $X, where X = temp value. Note the trailing comma - example: to set target temp to 70C, $70,
#delayed heating: Bx,y, where x = minutes, y = seconds. use C0 to cancel this function. Example: B2,0,
#set button press: T
 

#TBD: receipe mode options. - Connect controller characteristic seems to need 6 inputs for recipe mode.

###example recipe: simple 60 min recipe with no hop additions:
#R60,2,14.3,16.9,
#0,0,1,0,0,
#TEST SCHEDULE1
#0,0,0,0,
#65:60,
#75:10,

###other stuff to be confirmed:

#set mash step 1 to 65C for 60 minutes: 'a1,60,65,'


import bluepy.btle as btle
import sys

def pad_command(arg1):
  #print("in pad_command - got"+arg1)
  #GF Connect seems to require a max of 19 characters for commands
  outMsg = arg1.ljust(19)
  #print("in pad_command - output length is: "+str(len(outMsg)))
  return outMsg


def main():
#gf connector address: BB:A0:50:12:09:1G
  devAddr = sys.argv[1]
  print("Connecting to: {}".format(devAddr))
  controlCmd=pad_command(sys.argv[2])
  p = btle.Peripheral(devAddr)
  services = p.getServices()
  gfService = p.getServiceByUUID("0000cdd0-0000-1000-8000-00805f9b34fb")
  gfControlWriteChar = gfService.getCharacteristics("0003cdd2-0000-1000-8000-00805f9b0131")[0]
  #write to characteristic and don't wait for a response back from controller.
  gfControlWriteChar.write(controlCmd, False)
  #disconnect from controller
  p.disconnect()


if __name__ == '__main__':

 if len(sys.argv) < 3:
   sys.exit("Usage:\n  %s <mac-address> command" % sys.argv[0])

 main()

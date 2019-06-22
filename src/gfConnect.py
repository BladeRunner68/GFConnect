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


#Status notifications:
#T0,0,0,0,ZZZZZZZZ : timer?
#X60.0,21.1,ZZZZZZ : temp setpoint and temp status
#Y0,0,0,0,0,0,0,0, : guessing pump or heat
#W0,0,0,0,0,0,ZZZZ : guessing pump or heat

#TBD: receipe mode options. - Connect controller characteristic seems to need 6 inputs for recipe mode.

###example recipe: simple 60 min recipe with no hop additions:
#R60,2,14.3,16.9,
#0,0,1,0,0,
#TEST SCHEDULE1
#0,0,0,0,
#65:60,
#75:10,

### example recipe
#"R90,2,17,15.3,", # 5 min boil, 2 mash steps, 17 mash water, 15.3 sparge
#"0,0,1,0,0,",  # FIXME: what does this mean
#"RECIPEE RECIPEE REC", # Recipe name, max 19 chars, capital letters
#"22,3,0,0,", # 22 min hopstand, 3 boil additions, FIXME: remaining means?
#"60,",       # first boil addition
#"15,",       # second boil addition
#"10,",       # third boil addition
#"23:1,",    # first mash step
#"23:1,"]    # second mash step
 
###other stuff to be confirmed:

#set mash step 1 to 65C for 60 minutes: 'a1,60,65,'
# simple inquiry example

# "c2" : sets target to 0C and displays heat bar in display, not sure why.

import bluepy.btle as btle
import sys
import getopt
import time
import string

class ScanDelegate(btle.DefaultDelegate):
  def __init__(self):
    btle.DefaultDelegate.__init__(self)

  def handleDiscovery(self, dev, isNewDev, isNewData):
    if isNewDev:
      print("Discovered device %s" % dev.addr)
    elif isNewData:
      print("Received new data from %s" % dev.addr)

class NotifyDelegate(btle.DefaultDelegate):
  def __init__(self):
    btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
    # ... perhaps check cHandle
    # ... process 'data'
      print("cHandle: %s" % cHandle)
      print("data: %s" % data)

def pad_command(arg1):
  #GF Connect seems to require a max of 19 characters for commands
  outMsg = arg1.ljust(19)
  return outMsg

def scan():
  scanner = btle.Scanner().withDelegate(ScanDelegate())
  devices = scanner.scan(10.0)
  gfs = []
  for dev in devices:
    for (adtype, desc, value) in dev.getScanData():
      if desc == "Complete Local Name" and value == "Grain":
        gfs.append(dev.addr)
  del(scanner)
  return gfs

class Grainfather:
  GATTUUID = "0000cdd0-0000-1000-8000-00805f9b34fb"
  WRITEUUID = "0003cdd2-0000-1000-8000-00805f9b0131"
  NOTIFYUUID = "0003CDD1-0000-1000-8000-00805F9B0131"

  def __init__(self):
    self.mac = None
    self.periphial = None
    self.writechar = None
    self.notifychar = None

  def write(self, cmd):
    if self.periphial:
      self.writechar.write(pad_command(cmd.encode()), False)

  # FIXME: subscription not figured out yet
  def subscribe(self):
    if self.periphial:
      handle = self.notifychar.getHandle() + 1
      self.periphial.writeCharacteristic(handle, 
        b"\x02\x02\x00\x09\x00\x05\x00\x04\x00\x12\x0f\x00\x01\x00")

      for i in range(10):
          self.periphial.waitForNotifications(1.0)
          time.sleep(0.1)

  def unsubscribe(self):
    "FIXME: to be implemented"
    pass

  def set_temp(self, temp):
    self.write("$%i," % temp)

  def beep(self):
    self.write("!")

  def status(self):
    pass

  def toggle_pump(self):
    self.write("P")

  def quit_session(self):
    self.write("Q1")

  def cancel(self):
    self.write("C0,")

  def pause(self):
    self.write("G")

  def timer(self, minutes):
    self.write("S%i" % minutes)

  def toggle_heat(self):
    self.write("H")

  def temp_up(self):
    self.write("U")

  def temp_down(self):
    self.write("D")
  
  def delayed_heating(self, minutes):
    self.write("B%i,0," % minutes)

  def press_set(self):
    self.write("P")

  def connect(self, mac=""):
    if mac:
      self.mac = mac
    self.periphial = btle.Peripheral(self.mac)
    services = self.periphial.getServices()
    gfService = self.periphial.getServiceByUUID(self.GATTUUID)
    self.writechar = gfService.getCharacteristics(self.WRITEUUID)[0]
    self.notifychar = gfService.getCharacteristics(self.NOTIFYUUID)[0]
    self.periphial.setDelegate(NotifyDelegate())

  def disconnect(self):
    if self.periphial:
      self.periphial.disconnect()

  def __del__(self):
    self.disconnect()

  def set_recipe(self, name, boiltime, mashsteps, fillvol, spargevol,
      boiladditions, hopstand=0, spargeindicator=1, wateradditions=1):
    cmds = ["R%i,%i,%.1f,%1f," % (boiltime, len(mashsteps), fillvol,
      spargevol)]
    cmds.append("%i,%i,1,0,0," % (wateradditions, spargeindicator))
    cmds.append(name[0:19].upper())
    cmds.append("%i,%i,0,0," % (hopstand, len(boiladditions)))
    for a in boiladditions:
      cmds.append("%i," % a)
    for mashstep in mashsteps:
      cmds.append("%i:%i," % mashstep)

    for cmd in cmds:
      self.write(cmd)
      time.sleep(0.1)


if __name__ == '__main__':
  mac = ""
  optlist, args = getopt.getopt(sys.argv[1:], 'b:h', ['device=', 'help'])
  for opt, optval in optlist:
    if opt in ("-h", "--help"):
      sys.exit("Usage:\n  %s [-b<MAC>] [--device=<MAC>] [command]" % 
          sys.argv[0])
    if opt in ("-b", "--device"):
      mac=optval
  rawcmd = " ".join(args).encode()
  if not mac:
    mac = scan()[0]
  gf = Grainfather()
  gf.connect(mac)

  if rawcmd:
    gf.write(rawcmd)
  else:
    # Test some stuff
    #gf.quit_session()
    gf.toggle_pump()
    name = "test recipe with a too long name".upper()
    boiltime = 90
    mashsteps = ((45,10), (67, 60), (75, 10))
    fillvol = 16.7
    spargevol = 13.3
    boiladditions = (60, 30, 15)
    gf.set_recipe(name, boiltime, mashsteps, fillvol, spargevol, boiladditions)
    time.sleep(2)

  time.sleep(0.5)
  del(gf)


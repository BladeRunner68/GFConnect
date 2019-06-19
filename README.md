# GFConnect


GF Connect Bluetooth Controller Proof of concept


### Background

The Grainfather Connect controller uses Bluetooth Low Energy (BLE) technology for operation. Specifically, BLE GATT functionality is embedded on the controller to principally allow the Official Grainfather mobile application to control the boiler operation.  

Tech Highlights:

- BLE Service Broadcast name: Grain

- Main BLE GATT Service UUID: 0000cdd0-0000-1000-8000-00805f9b34fb

- Write Characteristic UUID: 0003cdd2-0000-1000-8000-00805f9b0131

- Notification (client read) UUID: 0003CDD1-0000-1000-8000-00805F9B0131

- All commands are single line write requests and each request needs to contain 19 characters - padded out with spaces


This proof of concept Python script allows for third party operation of the controller, bypassing the requirement to use the official Grainfather application.  This therefore opens up the Connect controller to other brewing applications and custom automation.



Command list so far:

- Timer set: Sx where x = mins to set - example: S1 for 1 minute timer, S5 for five minute timer.

- Cancel: C0

- Pause or resume: G

- Temp up: U

- Temp down: D

- Heat on/off toggle: H

- Pump on/off toggle: P

- Temperature set point: $X, where X = temp value. Note the trailing comma - example: to set target temp to 70C, $70,

- Delayed heating: Bx,y, where x = minutes, y = seconds. use C0 to cancel this function. Example: B2,0,

- Set button press: T


<b> ********************* Work-in-progress code - Use at your own risk! ********************* </b>


### Prerequisites

```
Raspberry Pi (v2 with bluetooth dongle, V3) or Linux host
```
```
Libs/packages: Bluez, bluepy, Python
```

### Installation/Set Up

```
TBD
```


### Work To be done

- More commands?

- Full Recipe mode

- Python refactor - maybe with threading so this is 'callable/triggerable'

- RPI image

- Node.js script

- Node-red workflow


## Authors

* **Simon Taylor** - *Initial Concept/POC script* - [BladeRunner68](https://github.com/BladeRunner68)

See also the list of [contributors](https://github.com/BladeRunner68/GFConnect/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


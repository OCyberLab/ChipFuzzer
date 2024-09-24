# ChipFuzzer: Towards Fuzzing Matter-based IoT Devices for Vulnerability Detection
This page documents the setup steps required to create a sample lab to perform vulnerability detection of Matter based IoT devices.

# 1. Hardware Requirements

The following table captures list of hardware kits required for building the lab. The device id will be used in commissioning and setup process as well as the vulnerability detection script.

|                                                              Hardware                                                               | Function                         | DeviceId |
|:-----------------------------------------------------------------------------------------------------------------------------------:|----------------------------------|---------|
|                                                       Ubuntu (22.04) Machine                                                        | Controller for experiment        | N/A|
|                     [nRF52840 Dongle](https://www.nordicsemi.com/Products/Development-hardware/nrf52840-dongle)                     | Open Thread Border Router (OTBR) | N/A |
|                         [nRF52840-DK](https://www.nordicsemi.com/Products/Development-hardware/nrf52840-dk)                         | Simulates Light Switch           |1|
|                         [nRF52840-DK](https://www.nordicsemi.com/Products/Development-hardware/nrf52840-dk)                         | Simulates Door Lock              |2|
|  [Nanoleaf Matter A19 Smart Bulb](https://nanoleaf.me/en-CA/products/essentials/bulbs/?category=A19-E26&standard=matter&size=each)  | Matter Light Bulb                |3|
|                          [Philips Hue Bridge](https://www.philips-hue.com/en-ca/p/hue-bridge/046677458478)                          | Matter Bridge |4|
| [Ikea TRÅDFRI](https://www.ikea.com/ca/en/p/tradfri-led-bulb-e26-1100-lumen-smart-wireless-dimmable-white-spectrum-globe-10489740/) | Zigbee Bulb | 4/2|

# 2. Prerequisites
Ensure following software is installed on the Ubuntu machine:
1. Docker
2. Visual Studio Code

# 3. Setup OTBR & Thread Network
Open Thread Border Router ([OTBR](https://openthread.io/guides/border-router)) is a reference implementation of the Thread Border Router component in a Matter cluster. OTBR is responsible for providing a bridge between IP based networks and the Thread mesh network. The nRF52840 Dongle will be used to deploy OTBR by configuring it with [OpenThread Radio Co-processor(RCP)](https://openthread.io/platforms/co-processor)

## 3.1. Setup Bootloader and RCP for nRF52840 Dongle
1. Clone OpenThread repository for NRF `git clone --recursive https://github.com/openthread/ot-nrf528xx.git`
2. Execute bootstrap script inside the repository `./script/bootstrap`. This will install all the required dependencies on your system
3. Build OpenThread for the nRF52840 USB Dongle: `./script/build nrf52840 USB_trans -DOT_BOOTLOADER=USB -DOT_THREAD_VERSION=1.2`
4. Convert image to `hex` format: `arm-none-eabi-objcopy -O ihex build/bin/ot-rcp build/bin/ot-rcp.hex`
5. Install nRF Util: `python3 -m pip install -U nrfutil`. This will install the utility in your ~/.local/bin directory, hence to use it you can either provide the full path to binary or add this directory to your PATH
6. Generate the RCP package:
   ```
    nrfutil pkg generate --hw-version 52 --sd-req=0x00 \
    --application build/bin/ot-rcp.hex \
    --application-version 1 build/bin/ot-rcp.zip
   ```
7. Connect the dongle via USB
8. Make sure the dongle is detected by executing `ls /dev | grep ACM`. The response should contain something like `ttyACM0`. If there are multiple devices listed with similar name, run the command before and after connecting the dongle to identify the exact name of this device.
9. Press the RESET button to make sure that the device is in DFU (Device Firmware Update) mode
10. Flash the device `nrfutil dfu usb-serial -pkg build/bin/ot-rcp.zip -p /dev/ttyACM0`. You might have to run this command as root to avoid permission errors.
11. After the RCP has been flashed on the dongle, this step does not need to be performed again. The firmware will be persisted even if the dongle is disconnected or the machine is powered down

 ## 3.2. Setup OTBR via Docker

 1. Ensure your dongle containing the RCP software is connected to Ubuntu machine. Following steps will assume that the dongle has been identified as `/dev/ttyACM0`
 2. Setup a IPv6 Docker Network `sudo docker network create --ipv6 --subnet fd11:db8:1::/64 -o com.docker.network.bridge.name=otbr0 otbr`
 3. Download OTBR Docker image: `docker pull nrfconnect/otbr:9185bda`
 4. Ensure IPv6 related kernel module is loaded: `sudo modprobe ip6table_filter`
 5. Start Docker container: 
    ```commandline
    docker run -it --rm --privileged --name otbr --network otbr -p 8080:80 \
    --sysctl "net.ipv6.conf.all.disable_ipv6=0 net.ipv4.conf.all.forwarding=1 net.ipv6.conf.all.forwarding=1" \
    --volume /dev/ttyACM0:/dev/radio nrfconnect/otbr:9185bda --radio-url "spinel+hdlc+uart:///dev/radio?uart-baudrate=1000000"
    ```
 6. Ensure OTBR Web UI is accessible by navigating to [http://localhost:8080/](http://localhost:8080/)
 7. Check status of OTBR: `sudo docker exec -it otbr sh -c "sudo service otbr-agent status"`

 ## 3.3 Setup Thread Network

 1. Navigate to OTBR Web UI [http://localhost:8080/](http://localhost:8080/)
 2. Select the 'Form' option on the sidebar
 3. Ensure that On-Mesh Prefix value is set to `fd11:22::/64` and click Create.
 4. Setup IP routing: `sudo ip -6 route add fd11:22::/64 dev otbr0 via fd11:db8:1::2`
 
# 4. Setup simulated matter devices
This section contains instructions to flash firmware on the development kits so they can simulate various matter devices

## 4.1. Setup nRF SDK
1. Download [nRF Connect for Desktop](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop/Download), all following commands in this section must be executed inside the directory that was created as a result of the clone
2. Click on `Install` button for Toolchain Manager. Once installed, clicked `Open`
3. Install the latest stable version of nRF Connect SDK. As of writing it was `v2.4.2`

## 4.2. Setup Switch
1. Click on Open VS Code in the Toolchain Manager
2. Click on nRF Connect Icon in the sidebar
   
   ![Preview](https://github.com/saurabhsjoshi/csi-6900-matter-iot/blob/c4ea956ea228b4aac9b7d065f13d2b24233cb246/images/4-1-nrf-icon-vscode.png)

 3. Click on Browse `samples` and search for `Matter Light Switch` and click `Open`
 4. Once the project is open, under the 'Applications' tab, click 'Add Build Configuration', in the next Dialog ensure nrf52840dk_nrf52840 is selected. Click `Build Configuration`
    ![Preview](https://github.com/saurabhsjoshi/csi-6900-matter-iot/blob/05ca4d7ef1378d44c66138de79f32dc4a59072c3/images/4-2-nrf-build.png)
 5. Once build is complete, connect one of the `nRF52840-DK` boards via USB, it should now be visible under 'Connected Devices' section
 6. Click on 'Flash' button under 'Actions' making sure your project and the board have been selected
    ![Preview](https://github.com/saurabhsjoshi/csi-6900-matter-iot/blob/3d64abfd967eb4beba3a1e1415a456dfbe221200/images/4-2-flash.png)
 7. The board is now flashed with firmware that makes the board simulate a Matter light switch. The `LED 2` on the board indicates the state of the switch. It can manually be toggled using `Button 2`.

## 4.3. Setup Matter Door Lock (nRF)
Follow the same steps as section 4.2, but in step 3 search for `Matter Lock`

## 4.4 Window Covering (SI Labs)
1. Download and install Simplicity Studio https://www.silabs.com/developers/simplicity-studio
2. Once installed, connect the EFR32xG24B board
3. Open Simplicity Studio and follow the setup process by selecting 'Installed by connecting device(s)'. This will show only the software that is suitable for the development board that has been connected.
4. Select the auto install mechanism and accept the licenses.
5. Once SDK(s) and required tools are installed. Select 'Example Projects and Demos'
6. Search for `Matter - SoC Window Covering over Thread`. Make sure that this is the 'Demo' version
7. Hit Run and this should flash the software required for SI Labs board to simulate a window covering
8. The LCD screen on the board should now show a QR code. Using a QR code scanning app on the phone get the matter code
9. Provision the device using `chip-tool` by running `./chip-tool pairing code-thread 6 hex:<otbr_dataset> MT:6FCJ142C00KA0648G00 --bypass-attestation-verifier true` Replace `<otbr_dataset>` with the data set obtained from the Thread Network in Step 3.3
10. Button 1 should act as the opening of the window cover, and button 2 is closed. The LCD screen should show the current position of the window cover. For more information, click on 'View Project Documentation' link in Simplicity Studio

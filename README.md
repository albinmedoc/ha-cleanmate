# Home Assistant Cleanmate Integration
Cleanmate is a popular robot vacuum cleaner in Sweden.

Right now there is no official documentation or API over how to control the robot. To develop this library the tcp request to and from the robot has been analyzed. 

<br>**Note:** The code has only been tested for the Cleanmate S995. Please make a Pull Request if you get it working with another model.

## How to get the authentication code
Currenly there is no easy way to get the authentication code (please let me know if there is).

The way to obtain a authentication code is to listen to a tcp packet when your phone sends a command to the robot. [Wireshark](https://www.wireshark.org/) is a great program to use for listening to network traffic.

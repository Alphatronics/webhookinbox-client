# Webhookinbox client for ARM Pelion

A python script that allows to open and track a remote webhook inbox locally. This fork is made specifically for parsing ARM Pelion (former Mbed Cloud Client) messages.

## How it works

![Architecture](mbed-webhookinbox-test.png)

## Usage

To start the webhook client application:

`$ python mbedwebhookinbox.py`

Press Ctrl+C to stop the client. Note that on Windows this may take a bit of time due to pending connections.

Next start the mbed cloud application:

`$ python pelionconsole.py`


## More info: 
* http://webhookinbox.com/
* https://cloud.mbed.com/docs/current/welcome/index.html

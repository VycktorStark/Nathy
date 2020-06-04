* * *
                 _   _       _   _                                                                                                                                
                | \ | | __ _| |_| |__  _   _                                                                                                                      
                |  \| |/ _` | __| '_ \| | | |                                                                                                                     
                | |\  | (_| | |_| | | | |_| |    By: Vycktor Stark                                                                                                               
                |_| \_|\__,_|\__|_| |_|\__, |    
                                       /___/

                
* * *

## Getting Started

These instructions will give you a copy of the project for you to use for development and testing purposes.

#### What is it?

Nathy is a virtual wizard that uses a Telegram API written in Python, its structure created by lib [Telepot](https://github.com/nickoala/telepot), and its plugins are made from the lib functions.
* * *

## Configuring bot

You should have your machine updated, and have Python (3.5 +) and pip (8.1+) installed, plus some libs: telepot, objectjson, requests, simplejson. What you need to do to install and use the project:

```
# Tested on Ubuntu 14.04, 15.04 and 16.04, Debian 7, Linux Mint 17.2

$ sudo apt-get update
$ sudo apt-get upgrade
## To install the libraries, just run run.sh and select option 5 or execute: 
$ sudo pip install -r requirements.txt
```
Cloning the repository:
```bash
# Cloning the repository and giving the permissions to start the initiation script

$ git clone https://github.com/VycktorStark/Nathy.git

```


**First of all, take a look at your bot settings:**

> • Make sure privacy is off (more information on the [Bots official FAQ page](https://core.telegram.org/bots/faq#what-messages-will-my-bot-get)). Send `/setprivacy` for [BotFather](http://telegram.me/BotFather) To check the current setting.

**Before doing anything, open the `config.py` file and with a text editor make the following changes:**

> • Set your Telegram ID to admin (in the `sudo` field).
>
> • Defina o ID do grupo Administradores (no campo `Chatsuporte`).
>
> • Set `TOKEN` with the authentication token received from the [BotFather](http://telegram.me/BotFather).
>

## Initialization process

To start the bot, execute `cd Nathy/ && sudo chmod 777 run.sh && ./run.sh`. To stop the bot, press `Ctrl + c` twice.

You can also start the bot with `cd Nathy/ && pyhton3 main.py`, but then it will not restart automatically.

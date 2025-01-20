## Project name
njuscript (ns) - polish mobile provider account-balance checker.  

## Table of contents
- [Project name](#project-name)
- [Table of contents](#table-of-contents)
- [General info](#general-info)
- [Technologies](#technologies)
- [Setup](#setup)
  - [Desktop](#desktop)
  - [Mobile](#mobile)
- [Usage](#usage)
  - [Desktop](#desktop-1)
  - [Mobile](#mobile-1)

## General info
Official nju mobile app is the worst app that I have ever used.
As a replacement, I have created a simple script which download and print most important account details (account balance and pending payments). It is definitely faster than official Nju Mobile app.

## Technologies
Code is pure Python 3.

Code was tested on following platform:
* Arch Linux (rolling release, Python 3.13.1)
* Android 14, Python 3.11.9

Packages required to run app are available in *requirements.txt*

## Setup

### Desktop
To use on desktop platforms (Linux, Windows) you will need to follow these steps:

1. Clone repository
2. Run following command to install required packages
    ```
    cd ns
    pip install -r requirements.txt
    ```

### Mobile
To use on Android you will need to follow these steps:  

1. Install following application from Google Play Store: [QPython](https://play.google.com/store/apps/details?id=org.qpython.qpy&hl=en)
2. Run QPython, tap "QPyPi" button and select "Pip Client"
3. Paste following command and run to install required packages:
    ```
    pip install -r https://raw.githubusercontent.com/mrachuta/ns/refs/tags/v1.2.0/requirements.txt
    ```
4. After installation, back to main screen and tap "Terminal"
5. Paste following command and run to get script:
    ```
    import os, requests; p = "{0}/scripts3/ns".format(os.environ["ANDROID_PUBLIC"]); os.makedirs(p, exist_ok=True); r = requests.get('https://raw.githubusercontent.com/mrachuta/ns/refs/tags/v1.2.0/ns.py'); file = open("{0}/ns.py".format(p), 'wb'); file.write(r.content); file.close()

    ```
6. Back to main screen and click buton at the top-middle of screen to open box with scripts
7. Hold your finger on the "ns.py" object and select "Create Shortcut" to make shortcut on desktop.
8. Run script from shortcut

## Usage

### Desktop
To run app just put on command line:
```
python ns.py
```

If you want to delete previous configuration (login and password), perform following command:
```
python ns.py -c
```
### Mobile
To run app just click on created link on main screen.  

To remove configuration:
1. Go to QPython's main screen
2. Hold your finger on the "ns.py" object and select "Run with params"
3. Add following param and run:
    ```
    -c
    ```
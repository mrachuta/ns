## Project name
ns (nju script) - polish mobile provider account-ballance checker.  

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Using](#using)
* [Thanks](#thanks)

## General info
Due to the worst app that I have ever used in my life for check current ballance, I have created a simple script which download and print all necessary informations. It is huge faster than official Nju Mobile app.

## Technologies
Code was written as a Python 3 code.

Code was tested on following platform:
* Debian Wheezy (kernel 4.18.0-2 amd64) with Python 3.6.6
* Widows 8.1 (x64) with Python 3.7.1
* Android 8.0 (Galaxy S7) with Python 3.6.4 (QPython)
* Android 8.1.1 (Galaxy XCover 4) with Python 3.6.6 (QPython)

Used libraries:
* Package and version   
* beautifulsoup4 4.6.3     
* bs4            0.0.1     
* certifi        2018.10.15
* chardet        3.0.4     
* idna           2.7       
* pip            18.1      
* requests       2.20.0    
* setuptools     40.5.0    
* urllib3        1.24.1    
* wheel          0.32.2   

## Setup

### Desktop
For using on desktop platforms (Linux, Windows) you will need only to install required packages.

### Android
For using on mobile-platforms (Android) you will need to follow these steps:  

1. Install applications as following (sugessted from Google Play Store):
```
QPython - Python for Android
QPy3.6 - Python 3.6 for QPython
```
2. Run QPython and:  
a) If you want to store login and password for faster check ballance, click "ALLOW" when app shows question about permission to files (otherwise you will receive error in app, when you will try to save data),  
b) switch interpreter to Python 3.6 (click "more" and chose Python interpreter - you will need also to download some resources, but app will do this automatically).  
3. Copy ns.py to following path:
```
/yourdevicememory/qpython/scripts3
```
4. Exctract site-packages.zip and copy site-packages folder to:
```
/yourdevicememory/qpython/lib/python3.6/
```
(if folder python3.6 not exists, create it).   
QPython has very limited packages database, for example: app can't compile some files for requests library and bs4 library using pip module, so my proposal is to copy precompiled files directly to specific path. QPython will use them without any problems.  
5. Run QPython and click on the icon on the middle-top of application, you will see the ns.py script.  
6. Long-click on ns.py, and add shocrout to desktop.  

## Using

### Desktop
To run app just put on command line:
```
python ns.py
```
If you want to delete previous configuration (login and password), add option 'clean':
```
python ns.py clean
```
### Mobile
To run app just click on created shocrout.  
To remove configuration, delete the *database.dat* file in /yourdevicememory/qpython/

## Thanks

Thanks to my girlfriend for his patience when I was coding.

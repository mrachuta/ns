#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-

import os
import ssl
import zipfile
import urllib.request
from platform import uname
from sys import version_info


def install_ns():

    """
    Downloading & installing necessary libraries and latest version of ns.py.
    Requirements:
    - Python 3.6 or higher,
    - Android device with ARM processor.
    """

    print(u'Instalator njuscript dla Android')
    print(u'-> Sprawdzam zależności:')

    python_ver = '.'.join(str(x) for x in version_info[:2])

    platform = str(uname())

    print(u'-> Platforma: {}'.format(platform))
    print(u'-> Wersja Pythona: {}'.format(python_ver))

    # Check if script is running on ARM device
    if 'arm' not in platform:

        print(u'-> Niewspierana platforma, uruchom na Android')

    elif python_ver <= '3.5:':

        print(u'-> Zaktualizuj Pythona do wersji >= 3.6 żeby zainstalować NjuScript')

    else:

        print(u'-> Rozpoczynam instalację, pobieram pakiet bibliotek')
        lib_url = 'https://github.com/mrachuta/dev-null/raw/master/site-packages.zip'
        zip_name = lib_url.split('/')[-1]
        urllib.request.urlretrieve(lib_url, zip_name)

        print(u'-> Instaluje pakiet bibliotek')
        with zipfile.ZipFile(zip_name, 'r') as zipped:
            zipped.extractall('/storage/emulated/0/qpython/lib/python{}/'.format(python_ver))
        os.remove(zip_name)

        print(u'-> Pobieram i instaluje ns.py')
        ns_url = 'https://raw.githubusercontent.com/mrachuta/ns/master/ns.py'
        urllib.request.urlretrieve(ns_url, '/storage/emulated/0/qpython/scripts3/ns.py')

        print(u'-> Instalacja zakończona sukcesem')


if __name__ == '__main__':

    # If PYTHONHTTPSVERIFY=0, create unverified SSL connection,
    # to prevent 'SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed'.
    if not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

    install_ns()


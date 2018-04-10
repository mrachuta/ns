# -*- coding: utf-8 -*-

"""
Small script to check account balance.
Only for polish mobile NJU customers.
"""

import re
import os
import sys
import time
import platform
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs4

det_os = str(platform.uname())

# File with hashed password

"""
If you have problem under Android's QPython3 with file-write permissions,
please check datafile variable, and compare path with path which is showed under QPpython3
settings -> FTP menu. In this path, QPython are able to write files. If necessary,
change the variable below.
"""

if ('Linux' and ('arm' or 'armv81')) in det_os:
    print('== URUCHOMIONY NA ANDROID ==')
    datafile = '/storage/emulated/0/qpython/database.dat'
else:
    print('== URUCHOMIONY NA DESKTOP ==')
    datafile = 'database.dat'

def clean():

    """
    This function search for the file 'datafile'
    and if exists, delete it
    """

    if os.path.exists(datafile) == True:
        os.remove(datafile)
    else:
        print('Nie ma takiego pliku!')

def encode_data(ulogin, upassword):

    """
    Function encode user login and user password.
    To do this, it needs two parameters.
    """

    print('-> Początek procedury hashowania')
    getcurrenttime = datetime.now()
    # Saving current time as float
    salt = float(getcurrenttime.strftime('%H%M%S'))
    #  Only for diagnostic purposes, enable this line if you want some debug
    #print(salt)
    # Convert each digit in user pass to unicode character
    hashpassword = [ord(c) for c in upassword]
    # Salting each unicode character
    saltedpassword = [salt * c for c in hashpassword]
    #  Only for diagnostic purposes, enable this line if you want some debug
    #print(saltedpassword)
    file = open(datafile, 'w')
    file.write(ulogin + str(saltedpassword) + ';' + str(salt / 2) + '\n')
    file.close()
    print('-> Koniec procedury hashowania')

def decode_data():

    """
    Function decode saved in 'datafile' characters
    """

    file = open(datafile, 'r')
    for line in file:
        ulogindecoded = (re.search('(.*)\[', line)).group(1)
        print('-> Początek procedury dehashowania')
        #  Only for diagnostic purposes, enable this line if you want some debug
        #print(ulogindecoded)
        # Search for salted password; next search for salt and decoding it
        saltedpassword = (re.search('\[(.*)\]', line)).group(1).split(',')
        saltencoded = float((re.search(';(.*)', line)).group(1))
        saltdecoded = float(saltencoded)*2
        # Decrypting password using decoded salt, saving as array, and next, as string
        decryptedpassword = [float(c) / saltdecoded for c in saltedpassword]
        upassworddecoded = ''.join([chr(int(c)) for c in decryptedpassword])
        print('-> Koniec procedury dehashowania')
        return ulogindecoded, upassworddecoded


def find_data(response, tagtype, tagparameter,
              tagname, valuetype):

    '''
    Using BeautifulSoup to scrap data (single value).
    html.parser is used, beacuse there is
    compability with qpython3 on android
    '''

    soup = bs4(response, 'html.parser')

    if valuetype != '':
        searchedvalue = soup.find(tagtype, {tagparameter : tagname})[valuetype]
    else:
        searchedvalue = soup.find(tagtype, {tagparameter : tagname})

    return searchedvalue

def find_all_data(response, tagtype, tagparameter,
                  tagname, valuetype):

    """
    Using BeautifulSoup to scrap data (multiple values);
    html.parser is used, beacuse there is
    compability with qpython3 on android
    """

    soup = bs4(response, 'html.parser')

    if valuetype != '':
        searchedvalues = soup.find_all(tagtype, {tagparameter : tagname})[valuetype]
    else:
        searchedvalues = soup.find_all(tagtype, {tagparameter : tagname})

    return searchedvalues

class EstablishConnection():

    """
    Main part of script; all functions in this class
    are connected directly with http-session, so the
    __init___ is verry necessary
    """

    def __init__(self):
        self.myheaders = requests.utils.default_headers()
        self.myheaders.update(
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            }
        )
        self.s = requests.Session()
        self.loginpage = self.s.get('https://www.njumobile.pl/logowanie',
                                    headers = self.myheaders)
        self.r = self.loginpage.text

        """
        To login on page, dynamic session value is necessary
        the function below, grab's this value
        """

        self.sessno = find_data(self.r, 'input', 'name',  '_dynSessConf', 'value')

    def login_nju(self, purelogin, purepassword):

        payloadlogin = {
            '_dyncharset': 'UTF-8',
            '_dynSessConf': self.sessno,
            '/ptk/sun/login/formhandler/LoginFormHandler.backUrl': '',
            '_D:/ptk/sun/login/formhandler/LoginFormHandler.backUrl': '',
            '/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn': '',
            '_D:/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn': '',
            'login-form': purelogin,
            '_D:login-form': '',
            'password-form': purepassword,
            '_D:password-form': '',
            'login-submit': 'zaloguj się',
            '_D:login-submit': '',
            '_DARGS': '/profile-processes/login/login.jsp.portal-login-form'
        }
        slogin = self.s.post(
            'https://www.njumobile.pl/logowanie?_DARGS=/profile-processes/login/login.jsp.portal-login-form#login-form-hash',
            data = payloadlogin, headers = self.myheaders)
        rlogin = slogin.text
        requestid = str(re.search('id=(.*)', (slogin.url)).group(1))
        loggedno = find_data(rlogin, 'span', 'class', 'sun-user-info__msisdn u-small-spacing-bottom u-small-spacing-top-l u-medium-left u-large-left', '')
        print('-> Udało się, zalogowany numer to: %s' % (loggedno.text))

        """
        IDK that this value below is necessary, but requests via browser sometimes have
        this value. I assumed that it will be good, when this value will be presented
        """

        return requestid

    def logout_nju(self):

        payloadlogout = {
            '_dyncharset': 'UTF-8',
            'logout-submit': 'wyloguj się',
            '_D:logout-submit': '',
            '_DARGS': '/core/v3.0/navigation/account_navigation.jsp.portal-logout-form'
        }
        slogout = self.s.post('https://www.njumobile.pl/?_DARGS=/core/v3.0/navigation/account_navigation.jsp.portal-logout-form',
                              data = payloadlogout, headers = self.myheaders)
        rlogout = slogout.text
        logoutconfirm = find_data(rlogout, 'span', 'class', 'sun-header__link-inner', '')

        if logoutconfirm is None:
            print('-> Coś poszło nie tak, nie wylogowałem')
        else:
            print('-> Ok wylogowano')

        self.s.cookies.clear()

    def stan_konta(self):

        """
        In first version, script tried to find data on scraped page;
        Now, data is scrapped from ajax-request, because in first load
        of Webpage, data is unreachable - ajax-request should be called
        "by hand"
        """

        repeat = 1
        while repeat < 5:

            print('-> Pobieram z ajaxowego requesta, próba %i' %(repeat))
            paramsajax = {
                'group': 'home-alerts-state-funds',
                'toGet': 'home-alerts-state-funds',
                'toUpdate': 'state-funds-infoservices',
                'pageId': '7800013',
                'actionUrl': '/mojekonto/stan-konta',
                'isPrepaid': '',
                'parentUrl': '/mojekonto',
                'isMobile': 'false',
                '_': '1518418491675'
            }
            headersajax = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
                'Host': 'www.njumobile.pl',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.njumobile.pl/mojekonto/stan-konta',
                'DNT': '1',
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3'
            }
            sbalanceajax  = self.s.get('https://www.njumobile.pl/ecare-infoservices/ajax',
                                       params = paramsajax, headers = headersajax)
            #  Only for diagnostic purposes, enable this line if you want some debug
            #print(sbalanceajax.url)
            rbalance = sbalanceajax.text
            #  Only for diagnostic purposes, enable this line if you want some debug
            #print(rbalance)
            reachedvalue = find_data(rbalance, 'div', 'class', 'box-slider-info', '')
            #  Only for diagnostic purposes, enable this line if you want some debug
            #print(reachedvalue)

            if reachedvalue is None:
                repeat = repeat+1
                time.sleep(2)
                if repeat > 4:
                    print('-> Nie mogę pobrać danych, spróbuj uruchomić ponownie :(')
            else:
                reachedvaluepure = re.search('<div class="box-slider-info">(.*)</div>', str(reachedvalue))
                #  Only for diagnostic purposes, enable this line if you want some debug
                #print(reachedvaluepure)
                break

        print('Aktualnie osiągnięty pułap płatności:%s\n' % (reachedvaluepure.group(1)))
        webpackage = find_data(rbalance, 'p', 'class', 'text-right', '')
        webpackagenumbers = ''.join((re.findall(r'\b\d+\b|\.|GB', str(webpackage))))
        webpackagelist = webpackagenumbers.split('GB')
        percentagemax = 100
        percentageusagepl = round((((float(webpackagelist[0])) * 100) / float(webpackagelist[1])), 0)
        percentagemaxdraw = int((percentagemax / 10) * 2)
        percentageusagedrawpl = int((percentageusagepl / 10) * 2)
        percentagegraphpl = ((percentageusagedrawpl * '#') + ((percentagemaxdraw - percentageusagedrawpl) * '-'))

        for char in percentagegraphpl:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.2)

        print('\nPozostało %i procent pakietu w kraju (%s GB z %s GB)' % (
        int(percentageusagepl), webpackagelist[0], webpackagelist[1]))
        percentageusageeu = round((((float(webpackagelist[2])) * 100) / float(webpackagelist[3])), 0)
        percentageusagedraweu = int((percentageusageeu / 10) * 2)
        percentagegrapheu = ((percentageusagedraweu * '#') + ((percentagemaxdraw - percentageusagedraweu) * '-'))

        for char in percentagegrapheu:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.2)

        print('\nPozostało %i procent pakietu w krajach EU (%s GB z %s GB)'
              % (int(percentageusageeu), webpackagelist[2], webpackagelist[3]))

    def finanse(self, requestidno):

        repeat = 1
        while repeat < 5:

            print('-> Pobieram z webowego requesta, próba %i' % (repeat))
            sfinance = self.s.post(
                ('https://www.njumobile.pl/mojekonto/faktury?_requestid=%s' %(requestidno)),
                headers = self.myheaders)
            rfinance = sfinance.text
            #  Only for diagnostic purposes, enable this line if you want some debug
            #print(sfinance.url)
            #print(sfinance.headers)
            cashdetails = find_all_data(rfinance, 'div', 'class', 'definition', '')
            invoices = find_all_data(rfinance, 'td', 'class', 'left-right-bg', '')

            if ((len(invoices) == 0) or (len(cashdetails) == 0)):
                repeat = repeat + 1
                time.sleep(2)
                if repeat > 4:
                    print('-> Nie mogę pobrać danych, spróbuj uruchomić ponownie :(')
            else:
                print('Aktualny stan konta: %s' % (cashdetails[0].text))
                print('Ostatnia wpłata: %s' % (cashdetails[1].text))
                print('\nNumer faktury  ::  Data wyst  ::  Okres od  ::  Okres do  '
                      ':: Kwota :: Pozostało ::   Typ   :: Za okres :: Status ::')

                """
                Code below prints invoices. Each invoice have 10 properties;
                not all are necessary. The last property are exchanged by new line symbol;
                Script print only three last invoices.
                """

                if len(invoices) < 8:
                    print('Brak faktur lub błąd')

                if len(invoices) == 10:
                    n = 0
                    while n <= 9 :

                        if n == 9:
                            sys.stdout.write('\n')
                            sys.stdout.flush()
                            time.sleep(0.0)
                        else:
                            sys.stdout.write(invoices[n].text + ' :: ' )
                            sys.stdout.flush()
                            time.sleep(0.0)

                        n = n+1

                elif len(invoices) == 20:
                    n = 0
                    while n <= 19:

                        if n == 9 or n == 19:
                            sys.stdout.write('\n')
                            sys.stdout.flush()
                            time.sleep(0.0)
                        else:
                            sys.stdout.write(invoices[n].text + ' :: ')
                            sys.stdout.flush()
                            time.sleep(0.0)

                        n = n + 1

                elif len(invoices) >= 30:
                    n = 0
                    while n <= 29:

                        if n == 9 or n == 19 or n == 29:
                            sys.stdout.write('\n')
                            sys.stdout.flush()
                            time.sleep(0.0)
                        else:
                            sys.stdout.write(invoices[n].text + ' :: ')
                            sys.stdout.flush()
                            time.sleep(0.0)

                        n = n + 1
                break

P1 = EstablishConnection()

"""
If argument 'clean' is added while run, the script clean the initial data
and allow login for a new user
"""

if __name__ == "__main__":

    if 'clean' in sys.argv[:]:
        print('= CZYSZCZENIE  KONFIGURACJI =')
        clean()
    else:
        print('-> Nie ma takiego argumentu, kontynuje')

"""
Interaction with user
"""

print('========= LOGOWANIE =========')

if os.path.exists(datafile) == True:
    print('-> Plik z danymi logowania istnieje, kontynuje')
    ulogindecoded, upassworddecoded = decode_data()
    requestidno = P1.login_nju(ulogindecoded, upassworddecoded)
else:
    ulogin = input('Podaj numer telefonu \n')
    upassword = input('Podaj hasło \n')

    while True:

        chose = input('Czy chcesz zachować dane logowania? [T]ak/[N]ie/[A]nuluj \n')

        if chose == 'T':
            encode_data(ulogin, upassword)
            requestidno = P1.login_nju(ulogin, upassword)
            break
        elif chose == 'N':
            print('-> OK, nie zapisuje')
            requestidno = P1.login_nju(ulogin, upassword)
            break
        elif chose == 'A':
            print('-> Zamykam')
            quit()

        print('Podałeś złą literkę')

print('======== STAN  KONTA ========')

P1.stan_konta()

print('========== FINANSE ==========')

P1.finanse(requestidno)

print('======= WYLOGOWYWANIE =======')

P1.logout_nju()
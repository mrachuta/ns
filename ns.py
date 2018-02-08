# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs4
import re
import time
import os
#import getpass
from datetime import datetime
import sys

datafile = 'database.dat'

def clean():

    if os.path.exists(datafile) == True:

        os.remove(datafile)

    else:

        print('Nie ma takiego pliku!')

def encode_data(ulogin, upassword):

    print('-> Początek procedury hashowania')
    getcurrenttime = datetime.now()
    salt = float(getcurrenttime.strftime('%H%M%S'))
    #print(salt) #only for diagnostic purposes
    hashpassword = [ord(c) for c in upassword]
    saltedpassword = [salt * c for c in hashpassword]
    #print(saltedpassword) #only for diagnostic purposes
    file = open(datafile, 'w')
    file.write(ulogin + str(saltedpassword) + ';' + str(salt / 2) + '\n')
    file.close()
    print('-> Koniec procedury hashowania')

def decode_data():

    file = open(datafile, 'r')

    for line in file:

        ulogindecoded = (re.search('(.*)\[', line)).group(1)
        print('-> Początek procedury dehashowania')
        #print(ulogindecoded)
        saltedpassword = (re.search('\[(.*)\]', line)).group(1).split(',')
        #saltedpasswordfloat = [float(c) for c in saltedpassword] #only for diagnostic purposes
        #print(saltedpasswordfloat) #only for diagnostic purposes
        saltencoded = float((re.search(';(.*)', line)).group(1))
        saltdecoded = float(saltencoded)*2
        #print(saltdecoded) #only for diagnostic purposes
        decryptedpassword = [float(c) / saltdecoded for c in saltedpassword]
        upassworddecoded = ''.join([chr(int(c)) for c in decryptedpassword])
        print('-> Koniec procedury dehashowania')
        return ulogindecoded, upassworddecoded


def find_data (response, tagtype, tagparameter, tagname, valuetype):

    soup = bs4(response, 'html.parser')

    if valuetype != '':

        searchedvalue = soup.find(tagtype, {tagparameter : tagname})[valuetype]

    else:

        searchedvalue = soup.find(tagtype, {tagparameter : tagname})

    return searchedvalue

def find_all_data (response, tagtype, tagparameter, tagname, valuetype):

    soup = bs4(response, 'html.parser')

    if valuetype != '':

        searchedvalues = soup.find_all(tagtype, {tagparameter : tagname})[valuetype]

    else:

        searchedvalues = soup.find_all(tagtype, {tagparameter : tagname})

    return searchedvalues

class EstablishConnection():

    def __init__(self):

        self.myheaders = requests.utils.default_headers()
        self.myheaders.update(
            {
                'User-Agent': 'Mozilla/5.0',
            }
        )
        self.s = requests.Session()
        self.s.get('https://www.njumobile.pl/logowanie', headers = self.myheaders)
        self.loginpage = self.s.get('https://www.njumobile.pl/logowanie', headers = self.myheaders)
        self.r = self.loginpage.text
        self.sessno = find_data(self.r, 'input', 'name',  '_dynSessConf', 'value')

    def login_nju(self, purelogin, purepassword):

        loginform = self.s.post(
            'https://www.njumobile.pl/logowanie?_DARGS=/profile-processes/login/login.jsp.portal-login-form#login-form-hash',
            headers = self.myheaders)

        payload = {
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

        s = self.s.post(
            'https://www.njumobile.pl/logowanie?_DARGS=/profile-processes/login/login.jsp.portal-login-form#login-form-hash',
            data = payload, headers = self.myheaders)

        response = s.text

        loggedno = find_data(response, 'span', 'class', 'icon-before-mobile infoline', '')

        print('-> Udało się, zalogowany numer to: %s' % (loggedno.text))

    def stan_konta(self):

        s = self.s.post('https://www.njumobile.pl/mojekonto/stan-konta', headers = self.myheaders)

        r = s.text

        reachedvalue = str(find_data(r, 'div', 'class', 'box-slider-info', ''))

        reachedvaluepure = re.search('<div class="box-slider-info">(.*)</div>', reachedvalue)

        print('Aktualnie osiągnięty pułap płatności:%s\n' % (reachedvaluepure.group(1)))

        webpackage = find_data(r, 'p', 'class', 'text-right', '')

        webpackagenumbers = ''.join((re.findall(r'\b\d+\b|\.|GB', str(webpackage))))

        webpackagelist = webpackagenumbers.split('GB')

        #print(webpackagelist) #only for diagnostic purposes

        percentagemax = 100

        percentageusagepl = round((((float(webpackagelist[0])) * 100) / float(webpackagelist[1])), 0)

        percentagemaxdraw = int((percentagemax / 10) * 2)
        percentageusagedrawpl = int((percentageusagepl / 10) * 2)

        # print(percentageusage, percentagemax) #only for diagnostic purposes

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

        print('\nPozostało %i procent pakietu w krajach EU (%s GB z %s GB)' % (
        int(percentageusageeu), webpackagelist[2], webpackagelist[3]))

    def finanse(self):

        s = self.s.post('https://www.njumobile.pl/mojekonto/faktury', headers = self.myheaders)

        r = s.text

        cashdetails = find_all_data(r, 'div', 'class', 'definition', '')

        print('Aktualny stan konta: %s' %(cashdetails[0].text))
        print('Ostatnia wpłata: %s' %(cashdetails[1].text))

        invoices = find_all_data(r, 'td', 'class', 'left-right-bg', '')
        print('\nNumer faktury  ::  Data wyst  ::  Okres od  ::  Okres do  :: Kwota :: Pozostało ::   Typ   :: Za okres :: Status ::')

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

        if len(invoices) == 20:

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

        if len(invoices) >= 30:

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

P1 = EstablishConnection()


if __name__ == "__main__":

    if sys.argv[1:] == 'c':

        print('= CZYSZCZENIE  KONFIGURACJI =')
        clean()

    else:

        print('-> Nie ma takiego argumentu, lece dalej!')

print('========= LOGOWANIE =========')

if os.path.exists(datafile) == True:

    print('-> Plik z danymi logowania istnieje, lecę dalej')
    ulogindecoded, upassworddecoded = decode_data()
    P1.login_nju(ulogindecoded, upassworddecoded)

else:

    ulogin = input('Podaj numer telefonu \n')
    upassword = input('Podaj hasło \n')

    while True:

        chose = input('Czy chcesz zachować dane logowania? [T]ak/[N]ie/[A]nuluj \n')

        if chose == 'T':

            encode_data(ulogin, upassword)
            P1.login_nju(ulogin, upassword)
            break

        elif chose == 'N':

            print('-> OK, nie zapisuje')
            P1.login_nju(ulogin, upassword)
            break

        elif chose == 'A':

            print('-> Zamykam')
            quit()

        print('Podałeś złą literkę')

print('======== STAN  KONTA ========')

P1.stan_konta()

print('========== FINANSE ==========')

P1.finanse()
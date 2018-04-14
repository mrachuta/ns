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
    data_file = '/storage/emulated/0/qpython/database.dat'
else:
    print('== URUCHOMIONY NA DESKTOP ==')
    data_file = 'database.dat'

def clean():

    """
    This function search for the file 'datafile'
    and if exists, delete it
    """

    if os.path.exists(data_file) == True:
        os.remove(data_file)
    else:
        print('Nie ma takiego pliku!')

def encode_data(
        u_login, u_password):

    """
    Function encode user login and user password.
    To do this, it needs two parameters.
    """

    print('-> Początek procedury hashowania')
    get_current_time = datetime.now()
    # Saving current time as float
    salt = float(get_current_time.strftime('%H%M%S'))
    #  Only for diagnostic purposes, enable this line if you want some debug
    #print(salt)
    # Convert each digit in user pass to unicode character
    hash_password = [ord(c) for c in u_password]
    # Salting each unicode character
    salted_password = [salt * c for c in hash_password]
    #  Only for diagnostic purposes, enable this line if you want some debug
    #print(salted_password)
    file = open(data_file, 'w')
    file.write(u_login + str(salted_password) + ';' + str(salt / 2) + '\n')
    file.close()
    print('-> Koniec procedury hashowania')

def decode_data():

    """
    Function decode saved in 'datafile' characters
    """

    file = open(data_file, 'r')
    for line in file:
        u_login_decoded = (re.search('(.*)\[', line)).group(1)
        print('-> Początek procedury dehashowania')
        #  Only for diagnostic purposes, enable this line if you want some debug
        #print(u_login_decoded)
        # Search for salted password; next search for salt and decoding it
        salted_password = (re.search('\[(.*)\]', line)).group(1).split(',')
        salt_encoded = float((re.search(';(.*)', line)).group(1))
        salt_decoded = float(salt_encoded)*2
        # Decrypting password using decoded salt, saving as array, and next, as string
        decrypted_password = [float(c) / salt_decoded for c in salted_password]
        u_password_decoded = ''.join([chr(int(c)) for c in decrypted_password])
        print('-> Koniec procedury dehashowania')
        return u_login_decoded, u_password_decoded

def find_data(
        response, tag_type, tag_parameter,
        tag_name, value_type):

    '''
    Using BeautifulSoup to scrap data (single value).
    html.parser is used, beacuse there is
    compability with qpython3 on android
    '''

    soup = bs4(response, 'html.parser')

    if value_type != '':
        searchedvalue = soup.find(tag_type, {tag_parameter : tag_name})[value_type]
    else:
        searchedvalue = soup.find(tag_type, {tag_parameter : tag_name})

    return searchedvalue

def find_all_data(
        response, tag_type, tag_parameter,
        tag_name, value_type):

    """
    Using BeautifulSoup to scrap data (multiple values);
    html.parser is used, beacuse there is
    compability with qpython3 on android
    """

    soup = bs4(response, 'html.parser')

    if value_type != '':
        searchedvalues = soup.find_all(tag_type, {tag_parameter : tag_name})[value_type]
    else:
        searchedvalues = soup.find_all(tag_type, {tag_parameter : tag_name})

    return searchedvalues

class EstablishConnection():

    """
    Main part of script; all functions in this class
    are connected directly with http-session, so the
    __init___ is verry necessary
    """

    def __init__(
            self):
        self.my_headers = requests.utils.default_headers()
        self.my_headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            }
        )
        self.s = requests.Session()
        self.login_page = self.s.get('https://www.njumobile.pl/logowanie',
                                    headers = self.my_headers)
        self.r = self.login_page.text

        """
        To login on page, dynamic session value is necessary
        the function below, grab's this value
        """

        self.sess_no = find_data(self.r, 'input', 'name',  '_dynSessConf', 'value')

    def login_nju(
            self, pure_login, pure_password):

        payload_login = {
            '_dyncharset': 'UTF-8',
            '_dynSessConf': self.sess_no,
            '/ptk/sun/login/formhandler/LoginFormHandler.backUrl': '',
            '_D:/ptk/sun/login/formhandler/LoginFormHandler.backUrl': '',
            '/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn': '',
            '_D:/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn': '',
            'login-form': pure_login,
            '_D:login-form': '',
            'password-form': pure_password,
            '_D:password-form': '',
            'login-submit': 'zaloguj się',
            '_D:login-submit': '',
            '_DARGS': '/profile-processes/login/login.jsp.portal-login-form'
        }
        s_login = self.s.post(
            'https://www.njumobile.pl/logowanie?_DARGS=/profile-processes/login/login.jsp.portal-login-form#login-form-hash',
            data = payload_login, headers = self.my_headers)
        r_login = s_login.text
        try:
            request_id = str(re.search('id=(.*)', (s_login.url)).group(1))
            logged_no = find_data(
                r_login, 'span', 'class',
                'sun-user-info__msisdn u-small-spacing-bottom u-small-spacing-top-l u-medium-left u-large-left', ''
            )

            """
            IDK that this value below is necessary, but requests via browser sometimes have
            this value. I assumed that it will be good, when this value will be presented
            """
            print('-> Udało się, zalogowany numer to: %s' % (logged_no.text))
        except AttributeError:
            print('-> ERROR: Na pewno podales poprawne dane logowania?')
            sys.exit(1)
        else:
            return request_id

    def logout_nju(
            self):

        payload_logout = {
            '_dyncharset': 'UTF-8',
            'logout-submit': 'wyloguj się',
            '_D:logout-submit': '',
            '_DARGS': '/core/v3.0/navigation/account_navigation.jsp.portal-logout-form'
        }
        s_logout = self.s.post(
            'https://www.njumobile.pl/?_DARGS=/core/v3.0/navigation/account_navigation.jsp.portal-logout-form',
            data = payload_logout, headers = self.my_headers
        )
        r_logout = s_logout.text
        logout_confirm = find_data(r_logout, 'span', 'class', 'sun-header__link-inner', '')

        if logout_confirm is None:
            print('-> ERROR: Coś poszło nie tak, nie wylogowałem')
            sys.exit(1)
        else:
            print('-> Ok wylogowano')

        self.s.cookies.clear()

    def stan_konta(
            self):

        """
        In first version, script tried to find data on scraped page;
        Now, data is scrapped from ajax-request, because in first load
        of Webpage, data is unreachable - ajax-request should be called
        "by hand"
        """

        repeat = 1
        while repeat < 5:

            print('-> Pobieram z ajaxowego requesta, próba %i' %(repeat))
            params_ajax = {
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
            headers_ajax = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
                'Host': 'www.njumobile.pl',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.njumobile.pl/mojekonto/stan-konta',
                'DNT': '1',
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3'
            }
            s_balance_ajax  = self.s.get(
                'https://www.njumobile.pl/ecare-infoservices/ajax',
                params = params_ajax, headers = headers_ajax
            )
            #  Only for diagnostic purposes, enable this line if you want some debug
            #print(sbalanceajax.url)
            r_balance = s_balance_ajax.text
            #  Only for diagnostic purposes, enable this line if you want some debug
            #print(rbalance)
            reached_value = find_data(r_balance, 'div', 'class', 'box-slider-info', '')
            #  Only for diagnostic purposes, enable this line if you want some debug
            #print(reachedvalue)

            if reached_value is None:
                repeat = repeat+1
                time.sleep(2)
                if repeat > 4:
                    print('-> ERROR: Nie mogę pobrać danych, spróbuj uruchomić ponownie :(')
            else:
                reached_value_pure = re.search('<div class="box-slider-info">(.*)</div>', str(reached_value))
                #  Only for diagnostic purposes, enable this line if you want some debug
                #print(reachedvaluepure)
                break

        print('Aktualnie osiągnięty pułap płatności:%s\n' % (reached_value_pure.group(1)))
        webpackage = find_data(r_balance, 'p', 'class', 'text-right', '')
        webpackage_numbers = ''.join((re.findall(r'\b\d+\b|\.|GB', str(webpackage))))
        webpackage_list = webpackage_numbers.split('GB')
        percentage_max = 100
        percentage_usage_pl = round((((float(webpackage_list[0])) * 100) / float(webpackage_list[1])), 0)
        percentage_max_draw = int((percentage_max / 10) * 2)
        percentage_usage_draw_pl = int((percentage_usage_pl / 10) * 2)
        percentage_graph_pl = ((percentage_usage_draw_pl * '#') + ((percentage_max_draw - percentage_usage_draw_pl) * '-'))

        for char in percentage_graph_pl:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.2)

        print('\nPozostało %i procent pakietu w kraju (%s GB z %s GB)' % (
        int(percentage_usage_pl), webpackage_list[0], webpackage_list[1]))
        percentage_usage_eu = round((((float(webpackage_list[2])) * 100) / float(webpackage_list[3])), 0)
        percentage_usage_draw_eu = int((percentage_usage_eu / 10) * 2)
        percentage_graph_eu = ((percentage_usage_draw_eu * '#') + ((percentage_max_draw - percentage_usage_draw_eu) * '-'))

        for char in percentage_graph_eu:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.2)

        print('\nPozostało %i procent pakietu w krajach EU (%s GB z %s GB)'
              % (int(percentage_usage_eu), webpackage_list[2], webpackage_list[3]))

    def finanse(
            self, request_id_no):

        repeat = 1
        while repeat < 5:

            print('-> Pobieram z webowego requesta, próba %i' % (repeat))
            s_finance = self.s.post(
                ('https://www.njumobile.pl/mojekonto/faktury?_requestid=%s' %(request_id_no)),
                headers = self.my_headers)
            r_finance = s_finance.text
            #  Only for diagnostic purposes, enable this line if you want some debug
            #print(s_finance.url)
            #print(s_finance.headers)
            cash_details = find_all_data(r_finance, 'div', 'class', 'definition', '')
            invoices = find_all_data(r_finance, 'td', 'class', 'left-right-bg', '')

            if ((len(invoices) == 0) or (len(cash_details) == 0)):
                repeat = repeat + 1
                time.sleep(2)
                if repeat > 4:
                    print('-> ERROR: Nie mogę pobrać danych, spróbuj uruchomić ponownie :(')
            else:
                print('Aktualny stan konta: %s' % (cash_details[0].text))
                print('Ostatnia wpłata: %s' % (cash_details[1].text))
                print(
                    '\nNumer faktury  ::  Data wyst  ::  Okres od  ::  Okres do  '
                      ':: Kwota :: Pozostało ::   Typ   :: Za okres :: Status ::'
                )

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

if os.path.exists(data_file) == True:
    print('-> Plik z danymi logowania istnieje, kontynuje')
    u_login_decoded, u_password_decoded = decode_data()
    request_id_no = P1.login_nju(u_login_decoded, u_password_decoded)
else:
    u_login = input('Podaj numer telefonu \n')
    u_password = input('Podaj hasło \n')

    while True:

        chose = input('Czy chcesz zachować dane logowania? [T]ak/[N]ie/[A]nuluj \n')

        if chose == 'T':
            encode_data(u_login, u_password)
            request_id_no = P1.login_nju(u_login, u_password)
            break
        elif chose == 'N':
            print('-> OK, nie zapisuje')
            request_id_no = P1.login_nju(u_login, u_password)
            break
        elif chose == 'A':
            print('-> Zamykam')
            quit()

        print('Podałeś złą literkę')

print('======== STAN  KONTA ========')

P1.stan_konta()

print('========== FINANSE ==========')

P1.finanse(request_id_no)

print('======= WYLOGOWYWANIE =======')

P1.logout_nju()
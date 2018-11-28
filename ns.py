#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-

import re
import os
import sys
import time
from platform import uname
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs4
import getpass
import argparse


def detect_platform():

    """
    Detecting platform and set data_file variable.
    Especially for mobile devices (Android), where files
    can be stored only under special path.
    """

    platform = uname()

    if 'Linux' in platform and 'arm' in platform:
        data_file = '/storage/emulated/0/qpython/database.dat'
        print(u'-> Wykryto platformę mobilną')
    else:
        data_file = 'database.dat'
        print(u'-> Wykryto platformę desktop')

    return data_file


def find_data(soup, tag_type, tag_parameter, tag_name, *value_type):

    """
    Find data using beautiful soup.
    Args:
        soup - parsed html data,
        tag_type - type of tag (for example: div, span etc.)
        tag_parameter - second parameter of tag (for example: class, id etc.)
        tag_name - name of parameter (for example header, footer)
        tag_value - optional parameter, specified value from tag.
    """

    if value_type:
        return soup.find(tag_type, {tag_parameter: tag_name})[value_type[0]]
    else:
        return soup.find(tag_type, {tag_parameter: tag_name})


def print_pretty(curr_value, max_value):

    """
    Print simple diagram using ASCII chars.
    Args:
         curr_value - value to be printed
         max_value - maximal value that can curr_value can reach

    Both values are recalculated to percentage value.
    One printed character represent 5%
    """

    curr_percentage = curr_value * 100.0 / max_value

    graph_curr = int(round(curr_percentage / 5.0, 0))
    graph_max = int(100.0 / 5.0)

    usage_graph = (graph_max * '#' + ((graph_max - graph_curr) * '-'))

    for char in usage_graph:
        sys.stdout.write(char)
        sys.stdout.flush()
        # change this value, to print diagram slower
        time.sleep(0.1)

    print(u' (dostępne: {:2.2f}%)'.format(curr_percentage))


class UserData:

    """
    Class for creating user object.
    Args:
        username - phone number,
        password - password set by user during account register,
        data_file - path to store encrypted login and password

    reset() - delete saved configuration - if exists,
    Method must be static, because calling this function without creating UserData object is necessary.
    encode_data() - encode password using char integer calculation, multiplied by salt.
    save_data() - write login, encoded password and salt to file,
    decode_data() - decode values stored in a configuration file (especially password).
    Method must be static, because calling this function without creating UserData object is necessary.
    """

    def __init__(self, username, password, data_file):
        self.username = username
        self.password = password
        self.data_file = data_file

    @staticmethod
    def reset():

        print(u'-> Usuwam domyślną konfigurację')

        data_file = detect_platform()

        if os.path.exists(data_file):
            os.remove(data_file)
        else:
            print(u'-> Nie ma takiego pliku!')

    def encode_data(self):

        print(u'-> Początek procedury hashowania')
        curr_time = datetime.now()
        # Save current time as float
        salt = float(curr_time.strftime('%H%M%S'))
        # Calculate integer for every char in password
        hashed_pass = [ord(c) for c in self.password]
        # Salt password
        salted_pass = [salt * c for c in hashed_pass]
        # Divide salt for make reading password harder
        salt = salt / 2
        return salt, salted_pass

    def save_data(self, salt, salted_pass):

        data_file = open(self.data_file, 'w')
        data_file.write(self.username + str(salted_pass) + str(salt) + '\n')
        data_file.close()

    @staticmethod
    def decode_data(data_file):

        data_file = open(data_file, 'r')
        for line in data_file:

            # Find username
            username_dec = re.search('(.*)\[', line).group(1)
            print('-> Początek procedury dehashowania')
            # Find salted password
            salted_pass = re.search('\[(.*)\]', line).group(1).split(',')
            # Find salt and prepare
            salt = float(re.search('\](.*)', line).group(1))*2
            # Divide every char by salt, change to integer and get ASCII code from integer
            password_dec = ''.join([chr(int(c)) for c in [float(c) / salt for c in salted_pass]])
            print('-> Koniec procedury dehashowania')
            return username_dec, password_dec


class Connection:

    """
    Class for communication with njumobile website.
    Every request is made during the same session.
    Args:
        none

    login() - open's login site and get _dynSessConf parameter, which is necessary to login.
    In next step data is send to remote server using POST request. The result is verified.
    logout() - logout from site. Result is verified.
    get_balance() - fetch data using ajax request. Sometimes first request is not successful;
    function will try 3 times to get the data.
    get_invoices() - fetch all invoices details from site.

    Important: to keep compatibility with function find_data(), all responses from serve should be first parsed
    by beautiful soup: bs4(response, 'html.parser')

    """

    def __init__(self):

        self.ns_headers = requests.utils.default_headers()
        self.ns_headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            }
        )
        self.ses = requests.Session()

    def login(self, username, password):

        login_site = self.ses.get('https://www.njumobile.pl/logowanie', headers=self.ns_headers)
        login_resp = login_site.text

        login_soup = bs4(login_resp, 'html.parser')

        # Get _dynSessConf value from site (prevention from automated logins)
        sess_no = find_data(login_soup, 'input', 'name',  '_dynSessConf', 'value')

        payload_login = {
            '_dyncharset': 'UTF-8',
            '_dynSessConf': sess_no,
            '/ptk/sun/login/formhandler/LoginFormHandler.backUrl': '',
            '_D:/ptk/sun/login/formhandler/LoginFormHandler.backUrl': '',
            '/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn': '',
            '_D:/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn': '',
            'login-form': username,
            '_D:login-form': '',
            'password-form': password,
            '_D:password-form': '',
            'login-submit': 'zaloguj się',
            '_D:login-submit': '',
            '_DARGS': '/profile-processes/login/login.jsp.portal-login-form'
        }

        login_req = self.ses.post('https://www.njumobile.pl/logowanie', data=payload_login, headers=self.ns_headers)
        login_req_resp = login_req.text

        # Check, that login is successful
        try:
            logged_soup = bs4(login_req_resp, 'html.parser')

            logged_no = find_data(
                logged_soup, 'span', 'class',
                'sun-user-info__msisdn u-small-spacing-bottom u-small-spacing-top-l u-medium-left u-large-left')

            print(u'-> Udało się, zalogowany numer to: {}'.format(logged_no.text))
        except AttributeError:
            sys.exit(u'-> BŁĄD: Na pewno podałeś poprawne dane logowania?')

    def logout(self):

        payload_logout = {
            '_dyncharset': 'UTF-8',
            'logout-submit': 'wyloguj się',
            '_D:logout-submit': '',
            '_DARGS': '/core/v3.0/navigation/account_navigation.jsp.portal-logout-form'
        }

        logout_req = self.ses.post(
            'https://www.njumobile.pl/?_DARGS=/core/v3.0/navigation/account_navigation.jsp.portal-logout-form',
            data=payload_logout, headers=self.ns_headers
        )

        logout_req_resp = logout_req.text
        logout_soup = bs4(logout_req_resp, 'html.parser')

        logout_confirm = find_data(logout_soup, 'span', 'class', 'sun-header__link-inner')

        # Check, that logout is successful
        if logout_confirm is None:
            sys.exit(u'-> BŁĄD: Coś poszło nie tak, nie wylogowałem')
        else:
            print(u'-> Wylogowano')

        self.ses.cookies.clear()

    def get_balance(self):

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

        # Try to get data 3 times
        repeat = 1
        while repeat < 4:

            bal_check = self.ses.post(
                'https://www.njumobile.pl/ecare-infoservices/ajax', params=params_ajax, headers=headers_ajax
            )
            bal_check_resp = bal_check.text

            if 'data okresu rozliczeniowego' not in bal_check_resp:
                repeat += 1
                time.sleep(2)
            else:
                return bal_check_resp

    def get_invoices(self):

        inv_check = self.ses.post('https://www.njumobile.pl/mojekonto/faktury', headers=self.ns_headers)
        inv_check_resp = inv_check.text

        return inv_check_resp


class Result:

    """
    Class for parsing data, and extract intresting values.
    Args:
        none

    balance_status() - find data in ajax response (current period, rate, rate description, cash amount and data-transfer package size).
    invoices_status() - find last three invoices, and all details for them. Present detailed data only
    for unpaid invoice.
    """

    def balance_status(self, html_resp):

        bal_soup = bs4(html_resp, 'html.parser')

        period_end = find_data(bal_soup, 'div', 'class', 'small-comment mobile-text-right tablet-text-right')
        rate = find_data(bal_soup, 'div', 'class', 'four columns tablet-six mobile-twelve')
        offer_title = rate.find("strong", recursive=False)
        curr_amount = find_data(bal_soup, 'div', 'class', 'box-slider-info')
        # Find all values in phrase (together with decimal values, if presented)
        curr_transfer = [float(x) for x in re.findall('\d{1,2}\.?\d{0,2}',
                                                      find_data(bal_soup, 'p', 'class', 'text-right').text)]
        print(u'= STAN KONTA =')
        print(u'-> Koniec okresu rozliczeniowego:{}'.format(period_end.text))
        print(u'-> Nazwa oferty: {}'.format(offer_title.text))
        print(u'-> Aktualnie osiagnięty pułap płatności:%s' % curr_amount.text)
        # Format all values to two decimal places
        print(u'-> Wykorzystanie internetu (kraj): dostępne {:2.{prec}f} GB z {:2.{prec}f} GB'.format(
            curr_transfer[0], curr_transfer[1], prec=2))
        print_pretty(curr_transfer[0], curr_transfer[1])
        print(u'-> Wykorzystanie internetu (EU): dostępne {:2.{prec}f} GB z {:2.{prec}f} GB'.format(
            curr_transfer[2], curr_transfer[3], prec=2))
        print_pretty(curr_transfer[2], curr_transfer[3])

    def invoices_status(self, html_resp):

        inv_soup = bs4(html_resp, 'html.parser')
        # Get last three invoices
        last_inv = [find_data(inv_soup, 'tr', 'id', 'id_abc-{}'.format(i)) for i in range(1, 4)]

        inv_list = []

        # Get details for each invoice
        for i in last_inv:

            inv_details = {}
            inv_headers = [
                u'nr dokumentu',
                u'data wystawienia',
                u'termin płatności',
                u'data zaksięgowania',
                u'kwota zapłacona',
                u'do zapłaty',
                u'typ dokumentu',
                u'za okres',
                u'status'
            ]

            for header in inv_headers:

                inv_details[header.title()] = find_data(i, 'td', 'data-title', header).text

            inv_list.append(inv_details)

        print(u'= FAKTURY =')
        counter = 1

        for inv in inv_list:

                print(u'-> Faktura {} z {}'.format(counter, len(inv_list)))

                # If invoice is not paid - show all details
                if inv['Status'] != u'zapłacona':

                    for key, value in inv.items():

                        print(u'|| {}: {}'.format(key, value))
                # If paid - show only number and status
                else:

                    print(u'|| Nr dokumentu: {}'.format(inv['Nr Dokumentu']))
                    print(u'|| Status: {}'.format(inv['Status']))

                counter += 1


def main():

    script = sys.argv[0]
    desc = u'NjuScript2, (c) 2018'

    # Argparse for better manage of arguments
    parser = argparse.ArgumentParser(prog=script, description=desc)
    parser.add_argument("-c", "--clean", action='store_true', help="clean configuration")
    options = parser.parse_args()

    print(desc)

    # Set data_file variable for static methods (class UserData)
    data_file = detect_platform()

    # Create Connection() object
    conn = Connection()

    # If requested, clean previously saved data (prepare for new user)
    if options.clean:

        UserData.reset()

    # If configuration data exists, use this credentials (class UserData object is not necessary)
    if os.path.exists(data_file):

        username_dec, password_dec = UserData.decode_data(data_file)
        conn.login(username_dec, password_dec)

    # Otherwise, create UserData object
    else:

        username = input(u'Podaj numer telefonu: ')
        password = getpass.getpass(u'Podaj hasło: ')

        user = UserData(username, password, data_file)

        while True:

            prompt = input(u'-> Czy chcesz zapisać dane? [T]ak/[N]ie/[A]nuluj: ').capitalize()

            if prompt == 'T':

                salt, salted_pass = user.encode_data()
                user.save_data(salt, salted_pass)
                username_dec, password_dec = user.decode_data(data_file)
                conn.login(username_dec, password_dec)
                break

            elif prompt == 'N':

                conn.login(username, password)
                break

            elif prompt == 'A':

                sys.exit(u'-> Anulowane przez użytkownika')

            print(u'Nie wybrałeś poprawnej wartości.')

    # Create objects necessary to show account details
    bal = conn.get_balance()
    inv = conn.get_invoices()
    res = Result()
    res.balance_status(bal)
    res.invoices_status(inv)
    conn.logout()


if __name__ == "__main__":

    main()


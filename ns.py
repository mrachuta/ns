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


def detect_platform():

    platform = uname()
    if 'Linux' in platform and 'arm' in platform:
        data_file = '/storage/emulated/0/qpython/database.dat'
        print(u'-> Wykryto platformę mobilną')
    else:
        data_file = 'database.dat'
        print(u'-> Wykryto platformę desktop')


def find_data(soup, tag_type, tag_parameter, tag_name, value_type):

    if value_type != '':
        return soup.find(tag_type, {tag_parameter: tag_name})[value_type]
    else:
        return soup.find(tag_type, {tag_parameter: tag_name})


def print_pretty(curr_value, max_value):

    curr_percentage = curr_value * 100.0 / max_value

    graph_curr = int(round(curr_percentage / 5.0, 0))
    graph_max = int(100.0 / 5.0)

    usage_graph = (graph_max * '#' + ((graph_max - graph_curr) * '-'))

    for char in usage_graph:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.3)

    print(u' (dostępne: {:2.2f}%)'.format(curr_percentage))


class UserData:

    def __init__(self):
        self.username = 'login'
        self.password = 'pass'

    def reset(self):
        pass

    def encode_data(self):
        pass

    def save_data(self):
        pass

    def decode_data(self):
        pass


class Connection:

    def __init__(self):

        self.ns_headers = requests.utils.default_headers()
        self.ns_headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            }
        )
        self.ses = requests.Session()

    def login(self, login, password):

        login_site = self.ses.get('https://www.njumobile.pl/logowanie', headers=self.ns_headers)
        login_resp = login_site.text

        login_soup = bs4(login_resp, 'html.parser')

        sess_no = find_data(login_soup, 'input', 'name',  '_dynSessConf', 'value')

        payload_login = {
            '_dyncharset': 'UTF-8',
            '_dynSessConf': sess_no,
            '/ptk/sun/login/formhandler/LoginFormHandler.backUrl': '',
            '_D:/ptk/sun/login/formhandler/LoginFormHandler.backUrl': '',
            '/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn': '',
            '_D:/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn': '',
            'login-form': login,
            '_D:login-form': '',
            'password-form': password,
            '_D:password-form': '',
            'login-submit': 'zaloguj się',
            '_D:login-submit': '',
            '_DARGS': '/profile-processes/login/login.jsp.portal-login-form'
        }

        login_req = self.ses.post('https://www.njumobile.pl/logowanie', data=payload_login, headers=self.ns_headers)
        login_req_resp = login_req.text

        try:
            logged_soup = bs4(login_req_resp, 'html.parser')

            logged_no = find_data(
                logged_soup, 'span', 'class',
                'sun-user-info__msisdn u-small-spacing-bottom u-small-spacing-top-l u-medium-left u-large-left', ''
            )

            print(u'-> Udało się, zalogowany numer to: {}'.format(logged_no.text))
        except AttributeError:
            print(u'-> ERROR: Na pewno podałeś poprawne dane logowania?')
            sys.exit(1)

    def logout(self):
        pass

    def get_ballance(self):

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

        repeat = 1
        while repeat < 5:

            ball_check = self.ses.post('https://www.njumobile.pl/ecare-infoservices/ajax', params=params_ajax, headers=headers_ajax)
            ball_check_resp = ball_check.text

            if 'data okresu rozliczeniowego' not in ball_check_resp:
                repeat += 1
                time.sleep(2)
            else:
                return ball_check_resp

    def get_invoices(self):

        inv_check = self.ses.post('https://www.njumobile.pl/mojekonto/faktury', headers=self.ns_headers)
        inv_check_resp = inv_check.text

        return inv_check_resp


class Result:

    def ballance_status(self, html_resp):

        ball_soup = bs4(html_resp, 'html.parser')

        period_end = find_data(ball_soup, 'div', 'class', 'small-comment mobile-text-right tablet-text-right', '')
        rate = find_data(ball_soup, 'div', 'class', 'four columns tablet-six mobile-twelve', '')
        offer_title = rate.find("strong", recursive=False)
        curr_amount = find_data(ball_soup, 'div', 'class', 'box-slider-info', '')
        curr_transfer = [float(x) for x in re.findall('\d{1,2}\.?\d{0,2}',
                                                      find_data(ball_soup, 'p', 'class', 'text-right', '').text)]
        print(u'= STAN KONTA =')
        print(u'-> Koniec okresu rozliczeniowego:{}'.format(period_end.text))
        print(u'-> Nazwa oferty: {}'.format(offer_title.text))
        print(u'-> Aktualnie osiagnięty pułap płatności:%s' % curr_amount.text)
        print(u'-> Wykorzystanie internetu (kraj): dostępne {:2.{prec}f} GB z {:2.{prec}f} GB'.format(
            curr_transfer[0], curr_transfer[1], prec=2))
        print_pretty(curr_transfer[0], curr_transfer[1])
        print(u'-> Wykorzystanie internetu (EU): dostępne {:2.{prec}f} GB z {:2.{prec}f} GB'.format(
            curr_transfer[2], curr_transfer[3], prec=2))
        print_pretty(curr_transfer[2], curr_transfer[3])

    def invoices_status(self, html_resp):

        inv_soup = bs4(html_resp, 'html.parser')
        last_inv = [find_data(inv_soup, 'tr', 'id', 'id_abc-{}'.format(i), '') for i in range(1, 4)]

        inv_list = []

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

                inv_details[header.title()] = find_data(i, 'td', 'data-title', header, '').text

            inv_list.append(inv_details)

        print(u'= FAKTURY =')
        counter = 1

        for inv in inv_list:

            print(u'-> Faktura {} z {}'.format(counter, len(inv_list)))

            for key, value in inv.items():

                print(u'{}: {}'.format(key, value))

            counter += 1


def main():

    detect_platform()
    conn = Connection()
    conn.login('login', 'pass')
    ball = conn.get_ballance()
    inv = conn.get_invoices()
    res = Result()
    res.ballance_status(ball)
    res.invoices_status(inv)


if __name__ == "__main__":

    main()


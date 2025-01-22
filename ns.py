#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import re
import os
import sys
import time
import getpass
import argparse
import requests
import base64
from datetime import datetime
from bs4 import BeautifulSoup as bs4


class EncoderDecoder:

    def __init__(self):
        self.username = None
        self.password = None
        self.username_encoded = None
        self.password_encoded = None
        self.salt = None

    def encode_data(self, username_input=None, password_input=None):

        if username_input is None or password_input is None:
            raise ValueError("BŁĄD: Parametr username i/lub password nie mogą być None")

        print("-> Początek procedury enkodowania")
        # Username as base64
        username_encoded = (base64.b64encode(username_input.encode("ascii"))).decode(
            "ascii"
        )
        # Calculate integer for every char in password
        password_encoded = [ord(c) for c in password_input]
        current_time = datetime.now()
        salt = current_time.strftime("%H%M%S")
        # Salt password and convert to string
        password_salted = ".".join([str(int(c) * int(salt)) for c in password_encoded])

        self.username_encoded = username_encoded
        self.password_encoded = password_salted
        self.salt = salt

    def decode_data(self, username_encoded, password_encoded, salt):
        self.username = (base64.b64decode(username_encoded.encode("ascii"))).decode(
            "ascii"
        )
        password_encoded_splitted = password_encoded.split(".")
        self.password = "".join(
            [
                chr(int(c))
                for c in [int(c) / int(salt) for c in password_encoded_splitted]
            ]
        )


class UserData(EncoderDecoder):

    def __init__(self):
        self.data_file = "database.dat"

    def _save_encoded_data_to_file(self):
        with open(self.data_file, "w") as f:
            f.write(
                "{0}&%{1}%&{2}".format(
                    self.username_encoded, self.password_encoded, self.salt
                )
            )

    def _get_encoded_data_from_file(self):
        f = open(self.data_file, "r")
        for line in f:
            # Find username
            self.username_encoded = re.search("^(.*)&%", line).group(1)
            # Find salted password
            self.password_encoded = re.search("&%(.*)%&", line).group(1)
            # Find salt
            self.salt = re.search("%&(.*)$", line).group(1)

    def get_credentials(self, username_input=None, password_input=None):
        if username_input is None or password_input is None:
            raise ValueError("BŁĄD: Parametr username i/lub password nie mogą być None")

        self.encode_data(username_input=username_input, password_input=password_input)

    def get_credentials_from_file(self):
        print("-> Znaleziono plik z zapisanymi danymi logowania")
        self._get_encoded_data_from_file()

    def save_credentials_to_file(self):
        print("-> Wybrano opcje zapisania danych logowania")
        self._save_encoded_data_to_file()

    def remove_data(self):
        print("-> Usuwam zapisane dane logowania")

        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        else:
            raise FileNotFoundError(
                "Błąd: Nie znaleziono pliku z zapisanymi danymi logowania"
            )


class NjuAccount(EncoderDecoder):

    def __init__(self, username_encoded=None, password_encoded=None, salt=None):
        EncoderDecoder.__init__(self)
        self.username_encoded = username_encoded
        self.password_encoded = password_encoded
        self.salt = salt
        self.ns_headers = requests.utils.default_headers()
        self.ns_headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
            }
        )
        self.ses = requests.Session()
        self.balance_output = None
        self.pending_payment_output = None

    def login(self):
        self.decode_data(self.username_encoded, self.password_encoded, self.salt)

        if self.username is None or self.password is None:
            raise ValueError("BŁĄD: Parametr username i/lub password nie mogą być None")

        login_site = self.ses.get(
            "https://www.njumobile.pl/logowanie", headers=self.ns_headers
        )
        login_resp = login_site.text

        login_soup = bs4(login_resp, "html.parser")

        # Get _dynSessConf value from source code
        sess_no = login_soup.find("input", {"name": "_dynSessConf"})["value"]

        payload_login = {
            "_dyncharset": "UTF-8",
            "_dynSessConf": sess_no,
            "/ptk/sun/login/formhandler/LoginFormHandler.backUrl": "",
            "_D:/ptk/sun/login/formhandler/LoginFormHandler.backUrl": "",
            "/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn": "",
            "_D:/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn": "",
            "phone-input": self.username,
            "_D:phone-input": "",
            "password-form": self.password,
            "_D:password-form": "",
            "login-submit": "zaloguj się",
            "_D:login-submit": "",
            "_DARGS": "/profile-processes/login/login.jsp.portal-login-form",
        }

        login_req = self.ses.post(
            "https://www.njumobile.pl/logowanie",
            data=payload_login,
            headers=self.ns_headers,
        )
        login_req_resp = login_req.text

        # Check if login is successful
        try:
            logged_soup = bs4(login_req_resp, "html.parser")

            logged_no = logged_soup.find("li", {"class": "cf title-dashboard-summary"})

            print("-> Udało się, zalogowany numer to: {}".format(logged_no.text))
        except AttributeError:
            sys.exit("BŁĄD: Na pewno podałeś poprawne dane logowania?")

    def logout(self):

        payload_logout = {
            "_dyncharset": "UTF-8",
            "logout-submit": "wyloguj się",
            "_D:logout-submit": "",
            "_DARGS": "/core/v3.0/navigation/account_navigation.jsp.portal-logout-form",
        }

        logout_req = self.ses.post(
            "https://www.njumobile.pl/?_DARGS=/core/v3.0/navigation/account_navigation.jsp.portal-logout-form",
            data=payload_logout,
            headers=self.ns_headers,
        )

        logout_req_resp = logout_req.text
        logout_soup = bs4(logout_req_resp, "html.parser")

        logout_confirm = logout_soup.find("span", {"class": "sun-header__link-inner"})

        # Check if logout is successful
        if logout_confirm is None:
            sys.exit("BŁĄD: Coś poszło nie tak, nie wylogowałem się poprawnie")
        else:
            print("-> Wylogowano")

        self.ses.cookies.clear()

    def get_balance(self):

        params_ajax = {
            "group": "home-alerts-state-funds",
            "toGet": "home-alerts-state-funds",
            "toUpdate": "state-funds-infoservices",
            "pageId": "7800013",
            "actionUrl": "/mojekonto/stan-konta",
            "parentUrl": "/mojekonto",
            "isMobile": "false",
        }

        headers_ajax = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Host": "www.njumobile.pl",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.njumobile.pl/mojekonto/stan-konta",
        }

        repeat = 1
        while repeat < 4:

            bal_check = self.ses.post(
                "https://www.njumobile.pl/ecare-infoservices/ajax",
                params=params_ajax,
                headers=headers_ajax,
            )
            bal_check_resp = bal_check.text

            if "data okresu rozliczeniowego" not in bal_check_resp:
                repeat += 1
                time.sleep(2)
            else:
                self.balance_output = bal_check_resp
                break

    def get_pending_payment(self):

        pend_paym_check = self.ses.post(
            "https://www.njumobile.pl/mojekonto", headers=self.ns_headers
        )
        pend_paym_check_resp = pend_paym_check.text

        self.pending_payment_output = pend_paym_check_resp


class Parser:

    def __init__(self, raw_input):
        self._raw_input = raw_input

    @staticmethod
    def print_pretty(current_value, max_value):

        current_value_percentage = current_value * 100.0 / max_value

        graph_current = int(round(current_value_percentage / 5.0, 0))
        graph_max = int(100.0 / 5.0)

        usage_graph = graph_current * "#" + ((graph_max - graph_current) * "-")

        for char in usage_graph:
            sys.stdout.write(char)
            sys.stdout.flush()
            # change this value, to print diagram slower
            time.sleep(0.1)

        print(" (dostępne: {:2.2f}%)".format(current_value_percentage))

    def print_balance_status(self):

        bal_soup = bs4(self._raw_input, "html.parser")

        period_end = bal_soup.find(
            "div", {"class": "small-comment mobile-text-right tablet-text-right"}
        )
        rate = bal_soup.find("div", {"class": "four columns tablet-six mobile-twelve"})
        offer_title = rate.find("strong", recursive=False)
        current_amount = bal_soup.find("div", {"class": "box-slider-info"})
        # Find all values in phrase (together with decimal values, if presented)
        current_transfer = [
            float(x)
            for x in re.findall(
                "\d{1,2}\.?\d{0,2}",
                bal_soup.find("p", {"class": "text-right"}).text,
            )
        ]
        print("= STAN KONTA =")
        print("-> Koniec okresu rozliczeniowego:{}".format(period_end.text))
        print("-> Nazwa oferty: {}".format(offer_title.text))
        print("-> Aktualnie osiagnięty pułap płatności: {}".format(current_amount.text))
        # Format all values to two decimal places
        print(
            "-> Wykorzystanie internetu (kraj): dostępne {:2.{prec}f} GB z {:2.{prec}f} GB".format(
                current_transfer[0], current_transfer[1], prec=2
            )
        )
        self.print_pretty(current_transfer[0], current_transfer[1])
        print(
            "-> Wykorzystanie internetu (EU): dostępne {:2.{prec}f} GB z {:2.{prec}f} GB".format(
                current_transfer[2], current_transfer[3], prec=2
            )
        )
        self.print_pretty(current_transfer[2], current_transfer[3])

    def print_pending_payment_status(self):

        pending_payment_soup = bs4(self._raw_input, "html.parser")
        # It's always right side of screen and last element
        pending_payment_col = pending_payment_soup.find_all(
            "div", {"class", "columns eight"}
        )[-1]
        pending_payment = re.findall(
            "\d+\.\d+",
            pending_payment_col.find(
                "li", {"class": "cf title-dashboard-summary"}
            ).text,
        )[0]
        print("= KWOTA DO ZAPŁATY =")
        print(
            "-> Aktualnie do zapłaty: {} zł".format(pending_payment).replace(".", ",")
        )


def main():

    script = sys.argv[0]
    desc = "njuscript 2.0.0 (c) 2025"

    # Argparse for better management of arguments
    parser = argparse.ArgumentParser(prog=script, description=desc)
    parser.add_argument(
        "-c", "--clean", action="store_true", help="clean configuration"
    )
    options = parser.parse_args()

    print(desc)

    ud = UserData()

    # If requested, clean previously saved data (prepare for new user)
    if options.clean:
        ud.remove_data()

    if os.path.exists(ud.data_file):
        ud.get_credentials_from_file()
    else:
        username = input("Podaj numer telefonu: ")
        password = getpass.getpass("Podaj hasło: ")

        ud.get_credentials(username_input=username, password_input=password)

        while True:

            prompt = input(
                "-> Czy chcesz zapisać dane? [T]ak/[N]ie/[A]nuluj: "
            ).capitalize()

            if prompt == "T":
                ud.save_credentials_to_file()
                break

            elif prompt == "N":
                break

            elif prompt == "A":
                sys.exit("-> Anulowane przez użytkownika")

            print("Nie wybrałeś poprawnej wartości.")

    na = NjuAccount(
        username_encoded=ud.username_encoded,
        password_encoded=ud.password_encoded,
        salt=ud.salt,
    )
    na.login()
    na.get_balance()
    na.get_pending_payment()
    Parser(na.balance_output).print_balance_status()
    Parser(na.pending_payment_output).print_pending_payment_status()
    na.logout()


if __name__ == "__main__":

    main()

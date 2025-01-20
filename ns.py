#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import re
import os
import sys
import time
import getpass
import argparse
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs4

def find_data(soup, tag_type, tag_parameter, tag_name, *value_type):
    """
    Find data using beautiful soup.
    Args:
        soup - parsed html data,
        tag_type - type of tag (for example: div, span etc.),
        tag_parameter - second parameter of tag (for example: class, id etc.),
        tag_name - name of parameter (for example header, footer),
        tag_value - optional parameter, specified value from tag.
    """

    if value_type:
        return soup.find(tag_type, {tag_parameter: tag_name})[value_type[0]]
    else:
        return soup.find(tag_type, {tag_parameter: tag_name})
    
def find_all_data(soup, tag_type, tag_parameter, tag_name):
    """
    Find data using beautiful soup.
    Args:
        soup - parsed html data,
        tag_type - type of tag (for example: div, span etc.),
        tag_parameter - second parameter of tag (for example: class, id etc.),
        tag_name - name of parameter (for example header, footer),
    """

    return soup.findAll(tag_type, {tag_parameter: tag_name})


def print_pretty(curr_value, max_value):
    """
    Print simple diagram using ASCII chars.
    Args:
         curr_value - value to be printed
         max_value - maximal value that can curr_value can reach

    Both values are recalculated to percentage value.
    One printed character represent 5%.
    """

    curr_percentage = curr_value * 100.0 / max_value

    graph_curr = int(round(curr_percentage / 5.0, 0))
    graph_max = int(100.0 / 5.0)

    usage_graph = graph_curr * "#" + ((graph_max - graph_curr) * "-")

    for char in usage_graph:
        sys.stdout.write(char)
        sys.stdout.flush()
        # change this value, to print diagram slower
        time.sleep(0.1)

    print(" (dostępne: {:2.2f}%)".format(curr_percentage))


class UserData:
    """
    Class creates user object.
    Args:
        username - phone number,
        password - password set by user during account registering,
        data_file - path to store encrypted login and password

    reset() - delete saved configuration - if exists.
    encode_data() - encode password using char-to-integer calculation, multiplied by salt.
    save_data() - write login, encoded password and salt to file,
    decode_data() - decode values stored in a configuration file (especially password).
    """

    def __init__(self, username, password, data_file):
        self.username = username
        self.password = password
        self.data_file = data_file

    @staticmethod
    def reset():

        print("-> Usuwam domyślną konfigurację")

        data_file = "database.dat"

        if os.path.exists(data_file):
            os.remove(data_file)
        else:
            print("-> Nie ma takiego pliku!")

    def encode_data(self):

        print("-> Początek procedury hashowania")
        curr_time = datetime.now()
        # Save current time as float
        salt = float(curr_time.strftime("%H%M%S"))
        # Calculate integer for every char in password
        hashed_pass = [ord(c) for c in self.password]
        # Salt password
        salted_pass = [salt * c for c in hashed_pass]
        # Divide salt to make password more complicated
        salt = salt / 2
        return salt, salted_pass

    def save_data(self, salt, salted_pass):

        data_file = open(self.data_file, "w")
        data_file.write(self.username + str(salted_pass) + str(salt) + "\n")
        data_file.close()

    @staticmethod
    def decode_data(data_file):

        data_file = open(data_file, "r")
        for line in data_file:

            # Find username
            username_dec = re.search("(.*)\[", line).group(1)
            print("-> Początek procedury dehashowania")
            # Find salted password
            salted_pass = re.search("\[(.*)\]", line).group(1).split(",")
            # Find salt and prepare (multiply by 2, because on decode_data() salt was divided by 2)
            salt = float(re.search("\](.*)", line).group(1)) * 2
            # Divide every char by salt, convert to integer and get ASCII code from integer
            password_dec = "".join(
                [chr(int(c)) for c in [float(c) / salt for c in salted_pass]]
            )
            print("-> Koniec procedury dehashowania")
            return username_dec, password_dec


class Connection:
    """
    Class creates connection to njumobile website.
    Every request is created within one session.
    Args:
        none

    login() - open login site and get _dynSessConf parameter, that is required to login.
    logout() - logout from site.
    get_balance() - fetch data using ajax request. Sometimes first request is not successful;
    function will try 3 times to get the data.
    get_invoices() - fetch all invoices-details from site.

    Important: to keep compatibility with function find_data(), all responses from server should be
    at beginning parsed by beautiful soup: bs4(response, 'html.parser')

    """

    def __init__(self):

        self.ns_headers = requests.utils.default_headers()
        self.ns_headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
            }
        )
        self.ses = requests.Session()

    def login(self, username, password):

        login_site = self.ses.get(
            "https://www.njumobile.pl/logowanie", headers=self.ns_headers
        )
        login_resp = login_site.text

        login_soup = bs4(login_resp, "html.parser")

        # Get _dynSessConf value from source code
        sess_no = find_data(login_soup, "input", "name", "_dynSessConf", "value")

        payload_login = {
            "_dyncharset": "UTF-8",
            "_dynSessConf": sess_no,
            "/ptk/sun/login/formhandler/LoginFormHandler.backUrl": "",
            "_D:/ptk/sun/login/formhandler/LoginFormHandler.backUrl": "",
            "/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn": "",
            "_D:/ptk/sun/login/formhandler/LoginFormHandler.hashMsisdn": "",
            "phone-input": username,
            "_D:phone-input": "",
            "password-form": password,
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

            logged_no = find_data(
                logged_soup, "li", "class", "cf title-dashboard-summary"
            )

            print("-> Udało się, zalogowany numer to: {}".format(logged_no.text))
        except AttributeError:
            sys.exit("-> BŁĄD: Na pewno podałeś poprawne dane logowania?")

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

        logout_confirm = find_data(
            logout_soup, "span", "class", "sun-header__link-inner"
        )

        # Check if logout is successful
        if logout_confirm is None:
            sys.exit("-> BŁĄD: Coś poszło nie tak, nie wylogowałem")
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
                return bal_check_resp

    def get_pending_payment(self):

        pending_payments_check = self.ses.post(
            "https://www.njumobile.pl/mojekonto", headers=self.ns_headers
        )
        pending_payments_check_resp = pending_payments_check.text
        
        return pending_payments_check_resp

class Result:


    """
    Class parse data and extract required values.
    Args:
        none

    balance_status() - find data in ajax response (current period, rate, rate description,
    cash amount and data-transfer package size).
    invoices_status() - find last three invoices, and all details for them.
    Provide detailed data only for unpaid invoice(s).
    """

    def balance_status(self, html_resp):

        bal_soup = bs4(html_resp, "html.parser")

        period_end = find_data(
            bal_soup,
            "div",
            "class",
            "small-comment mobile-text-right tablet-text-right",
        )
        rate = find_data(
            bal_soup, "div", "class", "four columns tablet-six mobile-twelve"
        )
        offer_title = rate.find("strong", recursive=False)
        curr_amount = find_data(bal_soup, "div", "class", "box-slider-info")
        # Find all values in phrase (together with decimal values, if presented)
        curr_transfer = [
            float(x)
            for x in re.findall(
                "\d{1,2}\.?\d{0,2}",
                find_data(bal_soup, "p", "class", "text-right").text,
            )
        ]
        print("= STAN KONTA =")
        print("-> Koniec okresu rozliczeniowego:{}".format(period_end.text))
        print("-> Nazwa oferty: {}".format(offer_title.text))
        print("-> Aktualnie osiagnięty pułap płatności: {}".format(curr_amount.text))
        # Format all values to two decimal places
        print(
            "-> Wykorzystanie internetu (kraj): dostępne {:2.{prec}f} GB z {:2.{prec}f} GB".format(
                curr_transfer[0], curr_transfer[1], prec=2
            )
        )
        print_pretty(curr_transfer[0], curr_transfer[1])
        print(
            "-> Wykorzystanie internetu (EU): dostępne {:2.{prec}f} GB z {:2.{prec}f} GB".format(
                curr_transfer[2], curr_transfer[3], prec=2
            )
        )
        print_pretty(curr_transfer[2], curr_transfer[3])

    def pending_payment_status(self, html_resp):
        pending_payment_soup = bs4(html_resp, "html.parser")
        # It's always right side of screen and last element
        pending_payment_col = find_all_data(pending_payment_soup, "div", "class", "columns eight")[-1]
        pending_payment = re.findall(
                "\d+\.\d+", find_data(pending_payment_col, "li", "class", "cf title-dashboard-summary").text)[0]
        print("= KWOTA DO ZAPŁATY =")
        print("-> Aktualnie do zapłaty: {} zł".format(pending_payment).replace('.', ','))

        
def main():

    script = sys.argv[0]
    desc = "njuscript 1.2.0 (c) 2025"

    # Argparse for better manage of arguments
    parser = argparse.ArgumentParser(prog=script, description=desc)
    parser.add_argument(
        "-c", "--clean", action="store_true", help="clean configuration"
    )
    options = parser.parse_args()

    print(desc)

    # Set data_file variable for static methods (class UserData)
    data_file = "database.dat"

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

        username = input("Podaj numer telefonu: ")
        password = getpass.getpass("Podaj hasło: ")

        user = UserData(username, password, data_file)

        while True:

            prompt = input(
                "-> Czy chcesz zapisać dane? [T]ak/[N]ie/[A]nuluj: "
            ).capitalize()

            if prompt == "T":

                salt, salted_pass = user.encode_data()
                user.save_data(salt, salted_pass)
                username_dec, password_dec = user.decode_data(data_file)
                conn.login(username_dec, password_dec)
                break

            elif prompt == "N":

                conn.login(username, password)
                break

            elif prompt == "A":

                sys.exit("-> Anulowane przez użytkownika")

            print("Nie wybrałeś poprawnej wartości.")

    # Create objects necessary to show account details
    balance = conn.get_balance()
    payment = conn.get_pending_payment()
    res = Result()
    res.balance_status(balance)
    res.pending_payment_status(payment)

    conn.logout()


if __name__ == "__main__":

    main()

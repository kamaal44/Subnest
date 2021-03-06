import sys
import os
import re
import json
import time
import signal
import tabulate
import argparse
import requests
from bs4 import BeautifulSoup as soup

__LOGO__ = """
      _/_/_/
   _/      _/    _/_/_/_/  _/_/_/    _/_/    _/_/_/_/_/_/_/
    _/_/  _/    _/_/    _/_/    _/_/_/_/_/_/_/      _/
       _/_/    _/_/    _/_/    _/_/          _/_/  _/
_/_/_/    _/_/_/_/_/_/  _/    _/  _/_/_/_/_/_/    _/_/

                                        {color}@hash3liZer/@an0nym0us
"""

class PULL:

    WHITE    = '\033[0m'
    PURPLE   = '\033[95m'
    CYAN     = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE     = '\033[94m'
    GREEN    = '\033[92m'
    YELLOW   = '\033[93m'
    RED      = '\033[91m'

    BGWHITE = '\033[107m'
    BGPURPLE = '\033[105m'
    BGCYAN   = '\033[46m'
    BGBLUE   = '\033[44m'
    BGGREEN  = '\033[42m'
    BGYELLOW = '\033[43m'
    BGRED    = '\033[41m'
    BGLGRAY  = '\033[47m'
    BGDGRAY  = '\033[100m'

    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    END       = '\033[0m'
    LINEUP    = '\033[F'

    REGEX_URL = r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"

    def __init__(self):
        if not self.support_colors:
            self.win_colors()

    def support_colors(self):
        plat = sys.platform
        supported_platform = plat != 'Pocket PC' and (plat != 'win32' or \
														'ANSICON' in os.environ)
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        if not supported_platform or not is_a_tty:
            return False
        return True

    def win_colors(self):
        self.WHITE = ''
        self.PURPLE = ''
        self.CYAN = ''
        self.DARKCYAN = ''
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.RED = ''
        self.BOLD = ''
        self.UNDERLINE = ''
        self.END = ''
        self.BGWHITE = ''
        self.BGPURPLE = ''
        self.BGCYAN   = ''
        self.BGBLUE   = ''
        self.BGGREEN  = ''
        self.BGYELLOW = ''
        self.BGRED    = ''
        self.BGLGRAY  = ''
        self.BGDGRAY  = ''

    def start(self, mess=""):
        print(self.RED + "[/] " + self.END + mess + self.END)

    def query(self, mess=""):
        print(self.BLUE + "[-] " + self.END + mess + self.END)

    def timer(self, mess):
        for letter in mess:
            sys.stdout.write(letter)
            sys.stdout.flush()
            time.sleep(0.001)

    def tab(self, key, mess, keylen=20):
        mess = str(mess)
        key  = str(key)

        template = "    -  {:%is} : " % keylen
        template = template.format(key)

        sys.stdout.write(self.BOLD)
        self.timer(template)
        sys.stdout.write(self.END)
        self.timer(mess)
        sys.stdout.write("\n")

    def is_url(self, vl):
        if re.search(self.REGEX_URL, vl, re.I):
            return self.UNDERLINE + vl + self.END
        return vl

    def end(self, mess):
        print(self.RED + "[\] " + self.END + mess + self.END)

    def error(self, mess=""):
        print(self.RED + "[-] " + self.END + mess + self.END)

    def exit(self, mess=""):
        sys.exit(self.RED + "[~] " + self.END + mess + self.END)

    def logo(self):
        global __LOGO__
        print(
            self.BOLD + self.RED + __LOGO__.format(color=self.GREEN) + self.END
        )

pull = PULL()

class RECON:

    GHEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://otx.alienvault.com/',
        'X-OTX-USM-USER': '0'
    }
    URL_GENERAL = "https://otx.alienvault.com/otxapi/indicator/domain/general/{domain}"
    URL_WHOIS   = "https://otx.alienvault.com/otxapi/indicator/domain/whois/{domain}"
    URL_HTTPSCAN= "https://otx.alienvault.com/otxapi/indicator/domain/http_scans/{domain}"
    URL_PDNS    = "https://otx.alienvault.com/otxapi/indicator/domain/passive_dns/{domain}"
    URL_RURL    = "https://otx.alienvault.com/otxapi/indicator/domain/url_list/{domain}?limit=50&page={page}"

    def __init__(self, prs):
        self.domain = prs.domain
        self.filter_all = prs.filter_all

    def enum_basic(self):
        url = self.URL_GENERAL.format(domain = self.domain)
        pull.query("Querying basic target info!")

        try:
            r = requests.get(url, headers=self.GHEADERS)
        except:
            r = None

        if r and r.status_code == 200:
            data = json.loads(r.text)
            sys.stdout.write("\n")
            pull.tab("Indicator", data["indicator"])
            pull.tab("Alexa", pull.is_url(data["alexa"]))
            pull.tab("Whois", pull.is_url(data["whois"]))
            pull.tab("Pulse Count", data["pulse_info"]["count"])
            if len(data["validation"]) and data["validation"][0]["source"] == "alexa":
                pull.tab("Alexa Rank", data["validation"][0]["message"].split(":").strip(" "))
            pull.tab("Sections", ", ".join(data["sections"]))
            sys.stdout.write("\n")
        else:
            pull.error("Error Requesting Basic Info RS [Invalid Code Received]")

    def enum_whois(self):
        url = self.URL_WHOIS.format(domain = self.domain)
        pull.query("Query WHOIS information about the target")

        try:
            r = requests.get(url, headers=self.GHEADERS)
        except:
            r = None

        if r and r.status_code == 200:
            data = json.loads(r.text)
            sys.stdout.write("\n")
            todisplay = data["data"]
            for key in todisplay:
                pull.tab(key["name"].lstrip(" ").rstrip(" "), key["value"])
            sys.stdout.write("\n")
        else:
            pull.error("Error Getting Whois Information RS [Invalid Code Received]")

    def enum_httpscan(self):
        url = self.URL_HTTPSCAN.format(domain = self.domain)
        pull.query("Querying normal HTTP Scans results against target")

        try:
            r = requests.get(url, headers=self.GHEADERS)
        except:
            r = None

        if r and r.status_code == 200:
            data = json.loads(r.text)
            sys.stdout.write("\n")
            todisplay = data["data"]
            for key in todisplay:
                key["value"] = str(key["value"])
                if "\n" not in key["value"] and len(key["value"]) < 50:
                    pull.tab(key["name"].lstrip(" ").rstrip(" "), key["value"], 40)
            sys.stdout.write("\n")
        else:
            pull.error("Error Getting HTTP Scan Information RS [Invalid Code Received]")

    def enum_pdns(self):
        url = self.URL_PDNS.format(domain = self.domain)
        pull.query("Querying Passive DNS Scans | Domains which point to {domain}".format(
            domain = pull.RED + self.domain + pull.END
        ))

        try:
            r = requests.get(url, headers=self.GHEADERS)
        except:
            r = None

        if r and r.status_code == 200:
            data = json.loads(r.text)
            sys.stdout.write("\n")
            todisplay = data["passive_dns"]
            fdata = []
            for key in todisplay:
                fdata.append([
                    key["record_type"],
                    key["asset_type"],
                    pull.BOLD + key["hostname"] + pull.END,
                    key["first"],
                    key["last"]
                ])
            pull.timer(
                tabulate.tabulate(fdata, headers=[
                    pull.BOLD + "Record Type",
                    "Asset Type",
                    "Hostname",
                    "First Seen",
                    "Last Seen" + pull.END
                ])
            )
            sys.stdout.write("\n\n")
        else:
            pull.error("Error Getting Passive DNS Information RS [Invalid Code Received]")

    def show_rurl(self, text):
        data = json.loads(text)["url_list"]
        for url in data:
            pull.tab(url["httpcode"], url["url"])

    def enum_rurl(self):
        url = self.URL_RURL.format(domain = self.domain, page=1)
        r = requests.get(url, headers=self.GHEADERS)
        if r.status_code == 200:
            data = json.loads(r.text)
            if data["actual_size"] > 0:
                result = data["actual_size"] / 50
                if not result.is_integer():
                    result += 2
                result = int(result)
                sys.stdout.write("\n")
                self.show_rurl(r.text)
                for page in range(2, result):
                    url = self.URL_RURL.format(domain = self.domain, page = page)
                    r = requests.get(url, headers=self.GHEADERS)
                    if r.status_code == 200:
                        self.show_rurl(r.text)
                sys.stdout.write("\n")
        else:
            pull.error("Error Getting Related URLS!")

    def engage(self):
        #self.enum_basic()
        #self.enum_whois()
        #self.enum_httpscan()
        #self.enum_pdns()
        #self.enum_rurl()
        return

class PARSER:

    DOMREGEX = r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]"

    def __init__(self, prs):
        self.domain = self.v_domain(prs.domain)
        self.output = self.v_output(prs.output)
        self.filter_all = prs.filter_all

    def v_domain(self, vl):
        if vl:
            if re.match(self.DOMREGEX, vl, re.I):
                return vl
            else:
                pull.exit("Invalid Domain Name Entered!")
        else:
            pull.exit("Domain Name Not Provided!")

    def v_output(self, vl):
        if vl:
            return vl
        return None

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--domain', dest="domain", default="", type=str, help="Target Domain")
    parser.add_argument('-o', '--output', dest="output", default="", type=str, help="Output file")
    parser.add_argument('-p', '--proxy' , dest="proxy" , default="", type=str, help="Proxy to use")
    parser.add_argument('--filter-all', dest="filter_all", default=False, action="store_true", help="Enumerate everything!")
    parser.add_argument('--filter-whois', dest="filter_whois", default=False, action="store_true", help="Filter Whois Information")

    parser = parser.parse_args()
    parser = PARSER(parser)

    pull.start("Recon initiated! Target Asset: {}".format(
        pull.GREEN + repr(parser.domain) + pull.END
    ))
    recon = RECON(parser)
    recon.engage()
    pull.end("Done!")

if __name__ == "__main__":
    pull.logo()
    main()

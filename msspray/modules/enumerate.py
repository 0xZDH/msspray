import argparse
import logging
import time
from datetime import datetime

from msspray.utils import (
    firefox,
    utils,
)
from msspray.utils.elements import Elements
from msspray.utils.logger import text_colors


def enumerate(args: argparse.Namespace):
    """Enumerate users

    :param args: arguments namespace
    """
    filename = f'enum_results.{datetime.utcnow().strftime("%Y%m%dT%H%M%Z")}.txt'
    logging.info(f"Writing enumeration results to: {filename}")

    valid_users = []
    requests = 0

    browser = firefox.FirefoxEngine(wait=args.wait, proxy=args.proxy, headless=args.headless)

    for username in args.username:
        requests += 1

        # This seems to helps with memory issues...
        browser.clear_cookies()

        # Load the web page - limit retries to 5
        retries = 5
        while True:
            try:
                browser.get(args.target)
                break

            except firefox.WebDriverException as e:
                if retries == 0:
                    logging.error(f"Firefox Engine Error: {e}")
                    exit(1)

                retries -= 1
                pass

        # Populate the username field and click 'Next'
        browser.populate_element(
            browser.find_element(Elements.username.type, Elements.username.value),
            username,
        )
        browser.click(browser.is_clickable(Elements.next.type, Elements.next.value))

        time.sleep(1)  # Ensure the previous DOM is stale

        # Handle invalid usernames
        if browser.find_element(Elements.usererror.type, Elements.usererror.value):
            if args.verbose:
                print(
                    f"[{text_colors.FAIL}INVALID{text_colors.ENDC}] "
                    f"{username}{' ' * 10}",
                    end="\r",
                )

            # Clear the element for next username
            browser.find_element(
                Elements.username.type, Elements.username.value
            ).clear()

        # If no username error, valid username
        else:
            logging.info(f"[{text_colors.OKGREEN}VALID{text_colors.ENDC}] {username}")
            utils.write_results(filename, username)

            valid_users.append(username)

        # Handle browser resets after every 5 username attempts
        # to deal with latency issues
        if requests == 10:
            browser = firefox.reset_browser(browser, args.wait, args.proxy, args.headless)
            requests = 0

        # Sleep/Jitter to throttle subsequent request attempts
        if args.sleep:
            utils.jitter_sleep(args.sleep, args.jitter)

    # Statistics
    print("\n")
    logging.info(f"Enumeration results saved to: {filename}")
    logging.info(f"Number of valid users:        {len(valid_users)}")

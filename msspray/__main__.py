import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
from random import randint

from msspray import __version__
from msspray.modules import (
    enumerate,
    spray,
)
from msspray.utils import (
    logger,
    utils,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Microsoft DOM-Based Enumeration and Password Sprayer - v{__version__}"
    )

    action_args = parser.add_argument_group(title="Actions")
    action_group = action_args.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "-e",
        "--enumerate",
        action="store_true",
        help="Perform username enumeration",
    )
    action_group.add_argument(
        "-s",
        "--spray",
        action="store_true",
        help="Perform password spraying",
    )

    primary_args = parser.add_argument_group(title="Primary Options")
    primary_args.add_argument(
        "-t",
        "--target",
        type=str,
        help="Authentication URL [Default: https://login.microsoftonline.com/]",
        default="https://login.microsoftonline.com/",
        required=False,
    )
    primary_args.add_argument(
        "-u",
        "--username",
        type=str,
        help="Comma delimited list or file containing usernames",
        required=True,
    )
    primary_args.add_argument(
        "-p",
        "--password",
        type=str,
        help="Comma delimited list or file containing passwords",
        required=False,
    )

    web_args = parser.add_argument_group(title="Web Configuration")
    web_args.add_argument(
        "--proxy",
        type=str,
        help="HTTP/S proxy (e.g. http://127.0.0.1:8080)",
        required=False,
    )
    web_args.add_argument(
        "--wait",
        type=int,
        help="Time to wait when looking for DOM elements (in seconds) [Default: 3]",
        default=3,
        required=False,
    )

    spray_args = parser.add_argument_group(title="Password Spraying Configuration")
    spray_args.add_argument(
        "--count",
        type=int,
        help="Number of password attempts per user before resetting the lockout timer",
        required=False,
    )
    spray_args.add_argument(
        "--lockout",
        type=float,
        help="Lockout policy reset time (in minutes)",
        required=False,
    )

    scan_args = parser.add_argument_group(title="Scan Configuration")
    scan_args.add_argument(
        "--sleep",
        type=int,
        choices=range(-1, 121),
        metavar="[-1, 0-120]",
        help=(
            "Throttle HTTP requests every `N` seconds. This can be randomized by "
            "passing the value `-1` (between 1 sec and 2 mins). [Default: 0]"
        ),
    )
    scan_args.add_argument(
        "--jitter",
        type=int,
        choices=range(0, 101),
        metavar="[0-100]",
        help="Jitter extends --sleep period by percentage given (0-100). [Default: 0]",
    )

    misc_args = parser.add_argument_group(title="Misc. Configuration")
    misc_args.add_argument(
        "--gui",
        action="store_true",
        help="Display the browser GUI (Default runs as headless)",
        required=False,
    )
    misc_args.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
        required=False,
    )
    misc_args.add_argument(
        "--debug",
        action="store_true",
        help="Debug output",
        required=False,
    )
    args = parser.parse_args()

    # If password spraying make sure we have all the information
    if args.spray:
        if not args.password:
            parser.error("the following arguments are required when password spraying: -p/--password")  # fmt: skip

        if not args.count:
            parser.error("the following arguments are required when password spraying: -c/--count")  # fmt: skip

        if not args.lockout:
            parser.error("the following arguments are required when password spraying: -l/--lockout")  # fmt: skip

    # Convert username(s) and password(s)
    if Path(args.username).is_file():
        args.username = utils.get_list_from_file(args.username)

    else:
        args.username = args.username.split(",")

    if args.password:
        if Path(args.password).is_file():
            args.password = utils.get_list_from_file(args.password)

        else:
            args.password = args.password.split(",")

    # Handle sleep randomization
    if args.sleep == -1:
        args.sleep = randint(1, 120)

    # Handle headless browser
    # GUI boolean will be the opposite value to what headless
    # should be (e.g. True GUI -> False headless)
    args.headless = not args.gui

    return args


def banner(args: argparse.Namespace):
    """Build and print banner

    :param args: argument namespace
    :param version: tool version
    """
    BANNER = "\n             *** msspray ***              \n"
    BANNER += "\n>----------------------------------------<\n"

    # Add version
    space = " " * (15 - len("version"))
    BANNER += "\n   > version%s:  %s" % (space, __version__)

    _args = vars(args)
    for arg in _args:
        if _args[arg]:

            value = _args[arg]
            space = " " * (15 - len(arg))

            # Manipulate values shown
            if arg in ["username", "password"]:
                value = len(value)

            BANNER += "\n   > %s%s:  %s" % (arg, space, str(value))

            # Add data meanings
            if arg == "username":
                BANNER += " usernames"

            if arg == "password":
                BANNER += " passwords"

            if arg == "count":
                BANNER += " passwords/spray"

            if arg == "lockout":
                BANNER += " minutes"

            if arg in ["wait", "sleep"]:
                BANNER += " seconds"

            if arg == "jitter":
                BANNER += "%"

    # Add timestamp for start of spray
    space = " " * (15 - len("start"))
    start_t = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    BANNER += "\n   > start%s:  %s" % (space, start_t)

    BANNER += "\n"
    BANNER += "\n>----------------------------------------<\n"

    print(BANNER)


def main():
    start = time.time()

    args = parse_args()

    logger.init_logger(args.debug)

    banner(args)

    if args.enumerate:
        enumerate.enumerate(args)

    elif args.spray:
        spray.spray(args)

    elapsed = time.time() - start
    logging.info(f"msspray executed in {elapsed:.2f} seconds.")

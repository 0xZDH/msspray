import logging
import time
import sys
from datetime import timedelta
from random import randint
from typing import (
    Any,
    List,
    Union,
)


def lockout_reset_wait(lockout: Union[int, float]):
    """Print a lockout timer to the screen.
    Reference: https://github.com/byt3bl33d3r/SprayingToolkit/blob/master/core/utils/time.py

    :param lockout: lockout time in minutes
    """
    delay = timedelta(hours=0, minutes=lockout, seconds=0)
    sys.stdout.write("\n\n")
    for remaining in range(int(delay.total_seconds()), 0, -1):
        sys.stdout.write(f"\r[*] Next spray in: {timedelta(seconds=remaining - 1)}")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n\n")


def get_list_from_file(f: str) -> List[Any]:
    """Read a file's lines into a list

    :param f: file to read into a list
    :returns: list of file lines
    """
    with open(f, "r") as f:
        l = [line.strip() for line in f if line.strip() not in [None, ""]]

    return l


def get_chunks_from_list(l: List[Any], n: int) -> List[Any]:
    """Yield chunks of a given size, N, from a provided list.

    :param l: original list to chunk
    :param n: size of list segments
    :yields: list segment
    """
    for i in range(0, len(l), n):
        yield l[i : i + n]


def check_last_chunk(sublist: List[Any], full_list: List[Any]) -> bool:
    """Identify if the current list chunk is the last chunk.
    This assumes the full_list was uniqued prior to chunking.

    :param sublist: sublist to compare to full_list
    :param full_list: complete list to check if sublist is in
    :returns: boolean if last chunk
    """
    if sublist[-1] == full_list[-1]:
        return True

    return False


def jitter_sleep(sleep: int, jitter: Union[int, float] = None):
    """Sleep for a designated amount of time with a given
    jitter percentage.

    :param sleep: seconds to sleep
    :param jitter: percentage to modify sleep each run
    """
    if sleep > 0:
        throttle = sleep
        if jitter and jitter > 0:
            throttle = sleep + int(sleep * float(randint(1, jitter) / 100.0))  # fmt: skip

        logging.debug(f"Sleeping for {throttle} seconds...")

        time.sleep(throttle)


def write_results(filename: str, username: str, password: str = None):
    """Write enumeration/spraying results to a file

    :param filename: output file name
    :param username: valid username
    :param password: valid password if spraying
    """
    with open(filename, "a") as f:
        if password:
            f.write(f"{username}:{password}\n")

        else:
            f.write(f"{username}\n")

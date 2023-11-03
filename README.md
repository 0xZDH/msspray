# **msspray**

> For educational, authorized and/or research purposes only.

See the related blog post: https://k3ramas.blogspot.com/2019/04/headless-browsers-for-password-spraying.html

This is a basic username enumeration and password spraying tool aimed at Microsoft Online authentication that renders in the DOM and requires the use of JavaScript to recognize page changes.

Currently, there is no concurrency built into the tool - it will run single-threaded.


## Setup

1. Install the Python dependencies

```bash
$ pip3 install -r requirements.txt
```

2. Install Firefox

```bash
# Linux
$ sudo apt install firefox-esr
```

3. Install Firefox's `geckodriver`

```bash
$ wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz
$ tar -xvf geckodriver-v0.32.0-linux64.tar.gz
$ export PATH=$PATH:$(pwd) # Add the current directory with the geckodriver to the PATH
```

> Ensure there are no firewall rules that block routing to localhost.
>
> Also, ensure that Firefox is up to date in order to set all of the required preferences.


## Usage

Perform username enumeration:<br>
`python3 msspray.py -e -t https://login.microsoftonline.com -u usernames.txt`

Perform password spray:<br>
`python3 msspray.py -s -t https://login.microsoftonline.com -u usernames.txt -p passwords.txt --count 2 --lockout 5`

```
usage: msspray.py [-h] (-e | -s) [-t TARGET]
                  -u USERNAME [-p PASSWORD]
                  [--proxy PROXY] [--wait WAIT]
                  [--count COUNT] [--lockout LOCKOUT]
                  [--sleep [-1, 0-120]] [--jitter [0-100]]
                  [--verbose] [--debug]

Microsoft DOM-Based Enumeration and Password Sprayer - v0.1.1

options:
  -h, --help            show this help message and exit

Actions:
  -e, --enumerate       Perform username enumeration

  -s, --spray           Perform password spraying

Primary Options:
  -t TARGET, --target TARGET
                        Authentication URL
                        [Default: https://login.microsoftonline.com/]

  -u USERNAME, --username USERNAME
                        Comma delimited list or file containing usernames

  -p PASSWORD, --password PASSWORD
                        Comma delimited list or file containing passwords

Web Configuration:
  --proxy PROXY         HTTP/S proxy (e.g. http://127.0.0.1:8080)

  --wait WAIT           Time to wait when looking for DOM elements (in seconds)
                        [Default: 3]

Password Spraying Configuration:
  --count COUNT         Number of password attempts per user before resetting the
                        lockout timer

  --lockout LOCKOUT     Lockout policy reset time (in minutes)

Scan Configuration:
  --sleep [-1, 0-120]   Throttle HTTP requests every `N` seconds. This can be randomized
                        by passing the value `-1` (between 1 sec and 2 mins).
                        [Default: 0]

  --jitter [0-100]      Jitter extends --sleep period by percentage given (0-100).
                        [Default: 0]

Misc. Configuration:
  --verbose             Verbose output

  --debug               Debug output
```


## Alternate Target Handling

While this tool by default targets Microsoft, functionality can be updated for different targets. The [Elements](msspray/utils/elements.py#L12) data structure contains the XPATH elements of each input field, button, and error label during the authentication process. This process, if updated for a different target, expects the following authentiaction flow:

1. The first page upon browsing to the provided target renders a username input field and a "next" button
    - If the username is invalid, a "user error" label is added to the DOM
2. Once the "next" button is clicked, a second page renders the password input field and the "login" button
    - If the credentials are invalid, an "invalid credentials" label is added to the DOM

Each element is defaulted to using XPATH lookups, but supports any of the following selenium lookup types:

```
ID
NAME
XPATH
LINK_TEXT
PARTIAL_LINK_TEXT
TAG_NAME
CLASS_NAME
CSS_SELECTOR
```

Identify the value for the given type being used, for example to find the XPATH value of a given object:

1. Right click the input field, button, or label and select `Inspect`
2. When the Inspector loads, right-click the highlighted HTML element and select: `Copy -> XPath`

**NOTE**: If any values are exempt (e.g. "work"), set the value to:
- `//*[@id="IGNORE_EXEMPT_FIELD"]` if using type "XPATH"
- `.IGNORE_EXEMPT_FIELD` if using type "CSS_SELECTOR"
- `IGNORE_EXEMPT_FIELD` if using any other type
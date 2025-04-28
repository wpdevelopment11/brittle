# brittle.py - Check links and find the broken ones

Read URLs from a file or stdin, one per line and check them.

Links are checked using a real browser. By default, it runs in the background.

The number of false positives is smaller compared to other HTTP clients, for example `curl`.

Links that trigger file downloads are properly handled. Files are not downloaded.

`brittle.py` can check URLs concurrently, only one concurrent request is made to a single domain though.
This prevents creating high load on servers and hitting rate limits.

Under the hood it uses [Playwrigth](https://playwright.dev/python/) for Chromium automation.

Tested on Windows and Linux.

## Install

```bash
git clone https://github.com/wpdevelopment11/brittle
cd brittle
python3 -m venv .venv
source .venv/bin/activate

# Install Playwright and a Chromium browser,
# which will be used to check URLs.
pip install playwright
playwright install chromium
```

## Example

The command below reads URLs from `urls.txt` and checks them concurrently, opening up to 5 pages in a browser at a time. Broken URLs are printed to the terminal. If the request doesn't complete in 10 seconds, the link is considered broken.

```bash
./brittle.py --workers 5 --timeout 10  urls.txt
```

You can pass `--verbose` flag to get the information about the current progress.
Broken links are written into `broken.txt`.

```bash
./brittle.py --verbose --workers 5 --timeout 10  urls.txt > broken.txt
```

Or you can run a browser in the foreground:

```bash
./brittle.py --headful --workers 5 --timeout 10  urls.txt
```

## Usage

```
brittle.py [-h] [-o OUTPUT] [-d DELAY] [-t TIMEOUT] [-p PROXY] [-u USER:PASS] [-f] [-v] [urls]

Check links using a browser to find the broken ones

Positional arguments:
  urls                  File to read the links from (default: stdin)

Options:
  -o, --output OUTPUT   File to write the broken links (default: stdout)
  -d, --delay DELAY     Delay in seconds between requests to the same domain
  -t, --timeout TIMEOUT
                        Timeout in seconds for request to complete (0 to disable timeout)
  -w, --workers WORKERS
                        How many concurrent requests to make
  -p, --proxy PROXY     Proxy server to use for requests (example: socks5://localhost:1080)
  -u, --proxy-user USER:PASS
                        Proxy username and password
  -f, --headful         Run browser in foreground
  -v, --verbose         Print HTTP statutes and URLs of completed requests to stderr
  -h, --help            Show this help message and exit
```

## Run tests

```bash
python3 -m unittest discover test
```

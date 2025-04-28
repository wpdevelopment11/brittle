#!/usr/bin/env python3

from collections import defaultdict
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Error

import argparse
import asyncio
import contextlib
import sys

async def check(urls, config):
    loop = asyncio.get_running_loop()
    async def open_in_browser():
        while domains:
            domain = domains.pop()
            for url in urls_map[domain]:
                next_time = loop.time() + config.delay
                # url=url hack to bind by value
                async def dw_handler(dw, url=url):
                    downloads.append(url)
                    await dw.cancel()
                page = await browser.new_page()
                page.on("download", dw_handler)
                try:
                    resp = await page.goto(url, wait_until="domcontentloaded", timeout=config.timeout)
                    if config.verbose:
                        print(f"{resp.status} {url}", file=sys.stderr)
                    if resp and resp.status > 399:
                        failures.append(url)
                except Error:
                    failures.append(url)
                finally:
                    await page.close()
                now = loop.time()
                await asyncio.sleep(max(0, next_time - now))

    failures = []
    downloads = []

    # Map from domain to URLs, to avoid concurrent access to the same domain
    urls_map = defaultdict(list)
    domain = lambda url: urlparse(url).hostname
    for url in urls:
        urls_map[domain(url)].append(url)
    domains = list(urls_map)

    async with async_playwright() as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch(headless=config.headless, proxy=config.proxy)
        workers = [open_in_browser() for i in range(config.workers)]

        await asyncio.gather(*workers)
        return sorted([f for f in failures if f not in downloads])

async def check_and_print(urls, output, config):
    broken = await check(urls, config)
    output.write("\n".join(broken) + "\n")

class Config():
    def __init__(self):
        self.verbose = False
        self.headless = True
        self.workers = 5
        self.delay = 3 # seconds
        self.timeout = 10000 # milliseconds
        self.proxy = None

def main(args):
    def open_file(file, mode, stdstream):
        if file is None:
            return contextlib.nullcontext(stdstream)
        else:
            return open(file, mode=mode, encoding="utf-8")

    def proxy_user(user):
        user = user.split(":", 1)
        if len(user) != 2:
            raise argparse.ArgumentTypeError("Wrong format")
        return user

    def workers(num):
        num = int(num)
        if (num == 0):
            raise argparse.ArgumentTypeError("Can't be zero")
        return abs(num)

    parser = argparse.ArgumentParser(description="Check links using a browser to find the broken ones")

    parser.add_argument("urls", nargs="?", help="File to read the links from (default: stdin)")
    parser.add_argument("-o", "--output", help="File to write the broken links (default: stdout)")
    parser.add_argument("-d", "--delay", help="Delay in seconds between requests to the same domain", type=float)
    parser.add_argument("-t", "--timeout", help="Timeout in seconds for request to complete (0 to disable timeout)", type=int)
    parser.add_argument("-w", "--workers", help="How many concurrent requests to make", type=workers)
    parser.add_argument("-p", "--proxy", help="Proxy server to use for requests (example: socks5://localhost:1080)")
    parser.add_argument("-u", "--proxy-user", metavar="USER:PASS", help="Proxy username and password", type=proxy_user)
    parser.add_argument("-f", "--headful", action="store_true", help="Run browser in foreground")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print HTTP statutes and URLs of completed requests to stderr")

    args = parser.parse_args(args)

    config = Config()
    config.verbose = args.verbose
    config.headless = not args.headful
    config.delay = max(0, args.delay) if args.delay is not None else config.delay
    config.timeout = max(0, args.timeout) * 1000 if args.timeout is not None else config.timeout
    config.workers = args.workers if args.workers is not None else config.workers

    if args.proxy is not None:
        config.proxy = {"server": args.proxy}
        user = args.proxy_user
        if user is not None:
            config.proxy["username"] = user[0]
            config.proxy["password"] = user[1]

    with (open_file(args.urls, "r", sys.stdin) as input,
          open_file(args.output, "w", sys.stdout) as output):
        urls = [line.removesuffix("\n") for line in input]
        asyncio.run(check_and_print(urls, output, config))

if __name__ == "__main__":
    main(sys.argv[1:])

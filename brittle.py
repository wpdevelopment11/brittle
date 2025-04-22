from collections import defaultdict
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Error

import asyncio

async def run():
    async def open_in_browser():
        while domains:
            domain = domains.pop()
            for url in urls_map[domain]:
                # url=url hack to bind by value
                async def dw_handler(dw, url=url):
                    downloads.append(url)
                    #print(f"in handler {url}")
                    await dw.cancel()
                page = await browser.new_page()
                page.on("download", dw_handler)
                try:
                    resp = await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                    print(resp.status)
                    if resp and resp.status > 399:
                        failures.append(url)
                except Error:
                    #print(f"in except {url}")
                    failures.append(url)
                finally:
                    await page.close()
        
    failures = []
    downloads = []

    with open("links.txt", encoding="utf-8") as file:
        urls = [line.removesuffix("\n") for line in file]
        # Map from domain to URLs, to avoid concurrent access to the same domain
        urls_map = defaultdict(list)
        domain = lambda url: urlparse(url).hostname
        for url in urls:
            urls_map[domain(url)].append(url)
        domains = list(urls_map)
    async with async_playwright() as playwright:
        result = open("broken2.txt", "w", encoding="utf-8")
        chromium = playwright.chromium
        browser = await chromium.launch(headless=False, proxy={"server": "socks5://localhost:9999"})
        workers = [open_in_browser() for i in range(5)]
        await asyncio.gather(*workers)

        result.write("\n".join(f for f in failures if f not in downloads))
        result.close()

asyncio.run(run())
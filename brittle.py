from playwright.async_api import async_playwright, Error

import asyncio

async def run():
    failures = []
    downloads = []

    with open("links.txt", encoding="utf-8") as file:
        urls = [line.removesuffix("\n") for line in file]
    async with async_playwright() as playwright:
        result = open("broken.txt", "w", encoding="utf-8")
        chromium = playwright.chromium
        browser = await chromium.launch(headless=False, proxy={"server": "socks5://localhost:9999"})
        for url in urls:
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
        await browser.close()

        result.write("\n".join(f for f in failures if f not in downloads))
        result.close()

asyncio.run(run())
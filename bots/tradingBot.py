import asyncio, json, os
from playwright.async_api import async_playwright

async def check_tickers(page, tickers, input_box):
    for ticker in tickers:
        await input_box.fill("", timeout=2000)
        await input_box.fill(ticker, timeout=2000)

        first_result = page.locator("div.itemInfoCell-oRSs8UQo.cell-oRSs8UQo").first
        second_result = page.locator("div.itemInfoCell-oRSs8UQo.cell-oRSs8UQo").nth(1)
        await first_result.wait_for(state="visible", timeout=5000)
        await first_result.hover()
        await asyncio.sleep(0.5)

        flag = page.locator("div.uiMarker-erqqoDve.markedFlag-oRSs8UQo").first
        try:
            await flag.wait_for(state="visible", timeout=2000)
            flag_classes = await flag.get_attribute("class")
            if "green-erqqoDve" not in flag_classes:
                await flag.click(force=True)
                await second_result.hover()
                print(f"Ticker {ticker} marked.")
            else:
                print(f"Ticker {ticker} already marked.")
        except:
            print(f"Ticker {ticker} has no flag, skipping.")


async def tradingMain():
    with open("./util/pw_cookies.json", "r") as f:
        cookies = json.load(f)

    tickers = []
    with open("./valid_tickers.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("Exchange:"):
                tickers.append(line)

    print(tickers)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto("https://tradingview.com/", wait_until="domcontentloaded")
        print("Loaded tradingview.com")
        
        search_box = page.locator("button", has_text="Поиск")
        await search_box.wait_for()
        await search_box.click()

        input_box = page.locator("input[placeholder*='Символ']")
        await input_box.wait_for(state="visible", timeout=2000)

        await check_tickers(page, tickers, input_box)

        await browser.close()

        if os.path.exists("./valid_tickers.txt"):
            os.remove("./valid_tickers.txt")
            print("Deleted valid_tickers.txt after processing.")

from playwright.async_api import async_playwright, expect
import asyncio

exchanges = ["nasd", "nyse"]
exchangesLength = len(exchanges)
valid_tickets = []

async def close_popups(page):
    try:
        popup = page.locator("#modal-elite-ad")
        if await popup.is_visible():
            print("Popup detected, closing...")
            await page.locator("#modal-elite-ad-close").click()
    except:
        pass

async def is_etf(page):
    etf = page.locator("h2", has_text="ETF")
    if await etf.count() > 0:
        return True
    return False

async def get_ticker_info(page):
    tickerName = (await page.locator("h1").first.text_content()).strip()
    priceString = await page.locator("strong").first.text_content()
    tickerPrice = float(priceString.replace(",", "").strip())
    etf = await is_etf(page)
    print(f"Ticker: {tickerName}, Price: {tickerPrice}, ETF: {etf}")
    return tickerName, tickerPrice, etf

async def process_ticker(page):
    tickerName, tickerPrice, etf = await get_ticker_info(page)
    if (40 <= tickerPrice <= 60) and not etf:
        valid_tickets.append(tickerName)

async def is_next_page_available(page):
    try:
        await expect(page.locator('.screener-pages.is-next')).to_be_visible()
        return True
    except:
        return False

async def scrape_exchange(page, exchange):
    global valid_tickets
    valid_tickets = []

    await page.goto("https://finviz.com/", wait_until="domcontentloaded")
    await close_popups(page)
    await page.get_by_role("link", name="Channel Up").click()
    await page.wait_for_selector("#screener-content")
    await page.get_by_role("link", name="Filters").click()
    await page.wait_for_selector("#fs_exch")
    await page.locator("#fs_exch").select_option(exchange)
    await page.locator("#fs_sh_price").select_option("o40")
    await page.wait_for_selector("#screener-content")

    while True:
        next_page_exists = await is_next_page_available(page)
        print(f"Next page exists: {next_page_exists}")

        images = page.locator("a img")
        count = await images.count()
        for i in range(count):
            img = images.nth(i)
            parent_link = img.locator("xpath=..")
            await close_popups(page)
            await parent_link.click()
            await page.wait_for_selector("h1")
            await process_ticker(page)
            await page.go_back(wait_until="domcontentloaded")
        
        if not next_page_exists:
            break

        next_page_link = page.locator(".is-next")
        await next_page_link.click()
        await page.wait_for_load_state("domcontentloaded")
    
    with open("valid_tickers.txt", "a", encoding="utf-8") as f:
        print(f"Writing to file for exchange: {exchange}")
        f.write(f"Exchange: {exchange}\n")
        for ticker in valid_tickets:
            f.write(ticker + "\n")

async def finvizMain():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Chrome/135.0.0.0", viewport={"width": 1920, "height": 1080})
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = await context.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080}) 

        for exchange in exchanges:
            print(f"Processing exchange: {exchange}")
            await scrape_exchange(page, exchange)
            print(f"Completed exchange: {exchange}")

        await context.tracing.stop(path="trace.zip")
        await browser.close()

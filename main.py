import json
from playwright.async_api import async_playwright
import asyncio
from telegram import Bot
from typing import Final

TOKEN: Final = '**'
CHAT_ID: Final = '**'  # Replace with your chat ID


bot = Bot(token=TOKEN)

base_url = "https://dexscreener.com"
cookies = [
    {"name": "__cf_bm", "value": "wtCiaaocZEL0DnNHTzzEEL4HhKT96A1B18JiPEe0cI0-1707131906-1-ASdpEb2K7VK3/JWF+6tLeYnlVc11c0HUk+knnX5VKFdRa/tejnTMs4QykoCXUahk5yrj9WI9Ob0fLoDv+R7NU277+8fI7wRQQ6qe16fR6FPr", "url": base_url},
    {"name": "_ga", "value": "GA1.1.1735481347.1707131807", "url": base_url},
    {"name": "_ga_532KFVB4WT", "value": "GS1.1.1707131807.1.1.1707131937.43.0.0", "url": base_url},
    {"name": "cf_clearance", "value": "7U2OoKosXnG61N0hOSBj1WVHREJJTZ0tsfGhf8Zow3U-1707131907-1-AeqjRSfcjCmJAEahwx+xuyAFSfobh+8BXwQxdZ+hrFj6wcmwPdaEY6zOUvumlNddjnyq2GSLBiG4NyYgkKx2D28=", "url": base_url},
    {"name": "chakra-ui-color-mode", "value": "dark", "url": base_url}
]
async def get_token_data_and_check_updates():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0")
        
        page = await context.new_page()
        await page.goto(base_url)
        
        await context.add_cookies(cookies)
        
        await page.goto("https://dexscreener.com/?rankBy=volume&order=desc&chainIds=solana&minLiq=7500&maxAge=12&min24HVol=50000")
        
        await page.wait_for_selector('.ds-dex-table-row', timeout=60000)

        # Send a message to the client when the bot starts tracking
        await bot.send_message(chat_id=CHAT_ID, text="The bot has started tracking new tokens.")

    while(True):
        token_elements = await page.query_selector_all('.ds-dex-table-row')
        initial_token_data = {}
        for element in token_elements:
            base_token_symbol = await element.query_selector('.ds-dex-table-row-base-token-symbol').inner_text()
            quote_token_symbol = await element.query_selector('.ds-dex-table-row-quote-token-symbol').inner_text()
            initial_token_data[base_token_symbol] = quote_token_symbol
        initial_token_count = len(initial_token_data)
        
        await asyncio.sleep(5)
        
        token_elements_updated = await page.query_selector_all('.ds-dex-table-row')
        updated_token_data = {}
        for element in token_elements_updated:
            base_token_symbol = await element.query_selector('.ds-dex-table-row-base-token-symbol').inner_text()
            quote_token_symbol = await element.query_selector('.ds-dex-table-row-quote-token-symbol').inner_text()
            updated_token_data[base_token_symbol] = quote_token_symbol
        updated_token_count = len(updated_token_data)
        
        if updated_token_count > initial_token_count:
            new_tokens = {k: v for k, v in updated_token_data.items() if k not in initial_token_data}
            await bot.send_message(chat_id=CHAT_ID, text=f"New token pairs added: {new_tokens}")

# Run the function
asyncio.run(get_token_data_and_check_updates())
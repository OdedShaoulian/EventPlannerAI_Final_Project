import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:8501")
        await page.wait_for_timeout(3000)
        
        # Click the chat input and submit a test query to generate chat bubbles
        chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
        if await chat_input.count() > 0:
            await chat_input.fill("Hello test")
            await chat_input.press("Enter")
            await page.wait_for_timeout(4000)
            
        # Print the outer HTML of any chat message elements
        chat_messages = page.locator('[data-testid="stChatMessage"]')
        count = await chat_messages.count()
        print(f"Found {count} chat messages.")
        for i in range(count):
            html = await chat_messages.nth(i).outer_html()
            print(f"--- Chat Message {i} ---")
            print(html[:1000]) # Print first 1000 chars of HTML
            
        await browser.close()

asyncio.run(main())

from playwright.async_api import async_playwright
from openai import AsyncAzureOpenAI
import asyncio
import random
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Azure OpenAI configuration from .env
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
AZURE_OPENAI_MODEL_DEPLOYMENT = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION") 

# Initialize Azure OpenAI client
client = AsyncAzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

SYSTEM_PROMPT = "Bạn là một trợ lý AI chuyên cung cấp những fact khoa học ngắn gọn, thú vị và dễ hiểu. Mỗi lần chỉ trả về 1 fact duy nhất, không thêm lời giải thích."
async def generate_message():
    try:
        response = await client.chat.completions.create(
            model=AZURE_OPENAI_MODEL_DEPLOYMENT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Hãy cho tôi một fact khoa học ngắn gọn, thú vị."}
            ],
            max_tokens=50,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating message: {e}")
        return ""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://chat.zalo.me")

        input("Đăng nhập Zalo web rồi nhấn Enter...")

        await page.wait_for_selector("input#contact-search-input", timeout=30000)
        await page.click("input#contact-search-input")
        await page.fill("input#contact-search-input", "đức duy cương tú")
        await asyncio.sleep(1)
        await page.press("input#contact-search-input", "Enter")
        await asyncio.sleep(2)

        while True:
            await page.wait_for_selector("div#richInput", timeout=30000)
            await page.click("div#richInput")

            await page.type("div#richInput", "@All ")
            await asyncio.sleep(1)
            await page.press("div#richInput", "Tab")
            message = await generate_message()
            await page.type("div#richInput", message)
            await page.press("div#richInput", "Enter")

            await asyncio.sleep(random.uniform(15, 30))

if __name__ == "__main__":
    asyncio.run(main())
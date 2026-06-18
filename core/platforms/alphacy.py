import asyncio
import os
import aiohttp
from aiohttp import web
from playwright.async_api import async_playwright

SITE_URL = "https://www.alphacyprus.com.cy/live"
PREFERRED = ["am8", "eu", "edge", "us"]

token_url = None
session_cookies = None
headers = {
    "Referer": "https://www.alphacyprus.com.cy/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
}

async def fetch_stream():
    global token_url, session_cookies

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        found = None

        async def on_response(response):
            nonlocal found
            url = response.url
            if ".m3u8" in url:
                for key in PREFERRED:
                    if key in url:
                        found = url
                        return

        page.on("response", on_response)
        await page.goto(SITE_URL)

        for _ in range(30):
            if found:
                break
            await asyncio.sleep(1)

        cookies = await context.cookies()
        session_cookies = {c["name"]: c["value"] for c in cookies}

        await browser.close()
        token_url = found


async def proxy_handler(request):
    global token_url, session_cookies

    path = request.match_info["path"]
    target = token_url.rsplit("/", 1)[0] + "/" + path

    async with aiohttp.ClientSession() as session:
        async with session.get(target, headers=headers, cookies=session_cookies) as resp:
            data = await resp.read()
            return web.Response(body=data, content_type=resp.headers.get("Content-Type"))


async def start_server():
    await fetch_stream()

    app = web.Application()
    app.router.add_get("/{path:.*}", proxy_handler)

    print("🚀 Proxy running at: http://localhost:8080/alphacy.m3u8")
    web.run_app(app, port=8080)


if __name__ == "__main__":
    asyncio.run(start_server())

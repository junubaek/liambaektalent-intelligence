import asyncio
from playwright.async_api import async_playwright

async def main():
    queries = ["M&A 담당자 찾아줘", "브랜드 마케터", "사업개발 BD"]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for q in queries:
            try:
                await page.goto("http://localhost:8000")
                await page.wait_for_load_state('networkidle')
                
                # set value via js
                await page.evaluate(f"document.querySelector('textarea').value = '{q}'")
                await page.evaluate("document.querySelector('textarea').dispatchEvent(new Event('input', { bubbles: true }))")
                
                # click run pipeline
                await page.evaluate("""
                    Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('RUN PIPELINE')).click()
                """)
                
                # wait for results to load
                await asyncio.sleep(6) # wait for render
                
                # count nodes
                # In the UI, the text says "FOUND X RELEVANT GRAPH NODES" or similar
                # Let's just grab the text containing "FOUND" or the count of candidate cards
                text_content = await page.evaluate("document.body.innerText")
                
                print(f"\\n--- Query: {q} ---")
                
                # find the line with "FOUND"
                for line in text_content.split('\\n'):
                    if "FOUND" in line.upper() and ("RELEVANT" in line.upper() or "CANDIDATE" in line.upper()):
                        print(line)
                        break
                else:
                    # count .bg-white.rounded-xl blocks which acts as candidate cards
                    cards = await page.evaluate("document.querySelectorAll('.bg-white.rounded-xl').length")
                    print(f"Found cards: {cards}")
            except Exception as e:
                print(f"Error for {q}: {e}")
                
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())

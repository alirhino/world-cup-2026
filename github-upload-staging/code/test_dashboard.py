"""Headless-browser test of the dashboard: capture JS errors, DOM state,
visible counts, console messages, and a screenshot."""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

HTML = Path(__file__).resolve().parent.parent / "Iran_WC2026_Fan_Dashboard.html"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await ctx.new_page()

        errors, console = [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: console.append(f"[{m.type}] {m.text}"))
        page.on("requestfailed", lambda r: errors.append(f"REQUEST FAILED: {r.url} -> {r.failure}"))

        url = f"file://{HTML}"
        print(f"navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2.5)  # let CDN script + JS init run

        print("\n=== page errors ===")
        for e in errors: print(" -", e)
        print("\n=== console (filtered) ===")
        for m in console: print(" ", m)

        # Inspect DOM state
        state = await page.evaluate("""() => ({
            hasHero: !!document.querySelector('.hero'),
            statTotal: document.getElementById('stat-total')?.textContent,
            statVia1: document.getElementById('stat-via-1st')?.textContent,
            statVia2: document.getElementById('stat-via-2nd')?.textContent,
            statTopOpp: document.getElementById('stat-top-opp')?.textContent,
            navButtons: document.querySelectorAll('.nav button').length,
            iranMatchCards: document.querySelectorAll('#iran-matches .match-card').length,
            otherMatchCards: document.querySelectorAll('#other-matches .match-card').length,
            groupTableRows: document.querySelectorAll('#group-table tbody tr').length,
            pathRows: document.querySelectorAll('#paths-list .path-card').length,
            chartCanvasExists: !!document.getElementById('finish-chart'),
            chartHasData: (() => {
                const c = document.getElementById('finish-chart');
                if (!c) return null;
                const ctx = c.getContext('2d');
                const id = ctx.getImageData(0, 0, c.width || 1, c.height || 1).data;
                return id.some(v => v !== 0);
            })(),
            chartJsLoaded: typeof window.Chart !== 'undefined',
            dataDefined: typeof window.DATA !== 'undefined',
        })""")

        print("\n=== DOM state ===")
        for k, v in state.items():
            print(f"  {k}: {v}")

        await page.screenshot(path="/tmp/dashboard_schedule.png", full_page=True)
        print("\nSchedule-tab screenshot: /tmp/dashboard_schedule.png")

        # Click each tab and validate it shows content + chart paints
        tab_results = {}
        for tab_id in ["group", "paths", "tickets", "method"]:
            await page.click(f'.nav button[data-tab="{tab_id}"]')
            await asyncio.sleep(0.6)
            visible = await page.evaluate(f"document.getElementById('tab-{tab_id}').classList.contains('active')")
            tab_results[tab_id] = visible
            await page.screenshot(path=f"/tmp/dashboard_{tab_id}.png", full_page=True)

        # Specifically check the chart pixels in a non-corner region after Group tab visible
        await page.click('.nav button[data-tab="group"]')
        await asyncio.sleep(1.0)
        chart_painted = await page.evaluate("""() => {
            const c = document.getElementById('finish-chart');
            if (!c || !c.getContext) return null;
            const ctx = c.getContext('2d');
            const w = c.width, h = c.height;
            const id = ctx.getImageData(w*0.3, h*0.5, 10, 10).data;
            return { w, h, hasPixels: id.some(v => v !== 0) };
        }""")
        print(f"\nChart canvas: {chart_painted}")
        print(f"Tab activation: {tab_results}")

        # Test filters on paths tab
        await page.click('.nav button[data-tab="paths"]')
        await asyncio.sleep(0.4)
        all_rows = await page.evaluate("document.querySelectorAll('#paths-list .path-card').length")
        await page.click('.filter-bar button[data-filter="1st"]')
        await asyncio.sleep(0.2)
        first_rows = await page.evaluate("document.querySelectorAll('#paths-list .path-card').length")
        await page.click('.filter-bar button[data-filter="2nd"]')
        await asyncio.sleep(0.2)
        second_rows = await page.evaluate("document.querySelectorAll('#paths-list .path-card').length")
        print(f"Path filters: all={all_rows}, 1st={first_rows} (expect 20), 2nd={second_rows} (expect 4)")

        # Expand the highest-probability path and screenshot it
        await page.click('.filter-bar button[data-filter="all"]')
        await asyncio.sleep(0.3)
        await page.evaluate("document.querySelectorAll('.path-card .path-header')[document.querySelectorAll('.path-card').length-1].click()")
        await asyncio.sleep(0.5)
        expanded_state = await page.evaluate("""() => {
            const cards = document.querySelectorAll('.path-card');
            const last = cards[cards.length-1];
            return {
                expandedCount: document.querySelectorAll('.path-card.expanded').length,
                lastCardExpanded: last.classList.contains('expanded'),
                chainSteps: last.querySelectorAll('.chain-step').length,
                groupMiniRows: last.querySelectorAll('.gm-row').length,
                hasGroupMini: !!last.querySelector('.group-mini')
            };
        }""")
        print(f"Expanded state: {expanded_state}")
        # Scroll to and screenshot the expanded card
        await page.evaluate("document.querySelector('.path-card.expanded').scrollIntoView({block:'center'})")
        await asyncio.sleep(0.3)
        await page.screenshot(path="/tmp/dashboard_expanded.png", full_page=False)
        print("Expanded-card screenshot: /tmp/dashboard_expanded.png")

        await browser.close()


asyncio.run(main())

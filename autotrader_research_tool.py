import streamlit as st
from playwright.sync_api import sync_playwright
import pandas as pd
import time

st.set_page_config(page_title="AutoTrader Research Tool", layout="wide")

st.title("🚗 AutoTrader Personal Research Tool")
st.caption("Paste an AutoTrader.co.za search URL. Personal research use only.")

search_url = st.text_input(
    "AutoTrader search results URL",
    placeholder="https://www.autotrader.co.za/cars-for-sale/..."
)

MAX_PAGES = 3
DELAY_SECONDS = 3


def scrape_listings(url):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_num in range(1, MAX_PAGES + 1):
            paged_url = f"{url}&page={page_num}"
            page.goto(paged_url, timeout=60000)

            page.wait_for_selector("article", timeout=15000)
            listings = page.query_selector_all("article")

            for listing in listings:
                try:
                    title = listing.query_selector("h2").inner_text()
                    price = listing.query_selector("[data-testid='price']").inner_text()
                    link = listing.query_selector("a").get_attribute("href")

                    results.append({
                        "Title": title,
                        "Price": price,
                        "Listing URL": "https://www.autotrader.co.za" + link
                    })

                except Exception:
                    continue

            time.sleep(DELAY_SECONDS)

        browser.close()

    return pd.DataFrame(results)


if st.button("🔍 Scrape Listings"):
    if not search_url.strip():
        st.error("Please paste a valid AutoTrader search URL.")
    else:
        with st.spinner("Scraping AutoTrader listings (this may take a minute)..."):
            df = scrape_listings(search_url)

        if df.empty:
            st.warning("No listings found.")
        else:
            st.success(f"Scraped {len(df)} listings")
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "⬇️ Download CSV",
                data=df.to_csv(index=False),
                file_name="autotrader_results.csv",
                mime="text/csv"
            )

"""
News fetcher using RSS feeds - no Playwright/Chromium needed.
Pulls real-time geopolitical/global news from major news outlets.
"""

import requests
import xml.etree.ElementTree as ET
import time

RSS_FEEDS = [
    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "type": "conflict"
    },
    {
        "name": "Reuters World",
        "url": "https://feeds.reuters.com/reuters/worldNews",
        "type": "market"
    },
    {
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "type": "conflict"
    },
    {
        "name": "DW News",
        "url": "https://rss.dw.com/rdf/rss-en-world",
        "type": "market"
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def _parse_feed(feed_info: dict, limit: int = 4) -> list:
    """Fetch and parse a single RSS feed."""
    results = []
    try:
        resp = requests.get(feed_info["url"], headers=HEADERS, timeout=8)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        # Standard RSS: channel > item
        items = root.findall(".//item")
        for item in items[:limit]:
            title_el = item.find("title")
            link_el = item.find("link")
            pub_el = item.find("pubDate")
            desc_el = item.find("description")

            title = title_el.text.strip() if title_el is not None and title_el.text else None
            link = link_el.text.strip() if link_el is not None and link_el.text else "#"
            pub = pub_el.text.strip() if pub_el is not None and pub_el.text else "Recently"
            
            # Clean up HTML tags from description if present
            desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
            import re
            desc = re.sub(r'<[^>]+>', '', desc)
            if len(desc) > 150: desc = desc[:147] + "..."

            # Shorten date string
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(pub)
                pub = dt.strftime("%d %b %H:%M")
            except Exception:
                pub = pub[:16]

            if title:
                # Classify type based on keywords
                tl = title.lower()
                category = "conflict" if any(w in tl for w in [
                    "war", "strike", "clash", "military", "troops", "attack",
                    "missile", "sanction", "kill", "bomb", "explosion", "conflict"
                ]) else "market"

                results.append({
                    "title": f"[{feed_info['name']}] {title}",
                    "description": desc,
                    "type": category,
                    "time": pub,
                    "url": link
                })
    except Exception as e:
        print(f"RSS fetch failed for {feed_info['name']}: {e}")

    return results


class BrowserScraper:
    """Fetches geopolitical news from RSS feeds of major outlets."""

    def scrape_global_news(self, limit_per_feed: int = 4) -> list:
        """Return combined list of latest geopolitical articles from all RSS feeds."""
        all_articles = []
        for feed in RSS_FEEDS:
            all_articles.extend(_parse_feed(feed, limit=limit_per_feed))
        return all_articles

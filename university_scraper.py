
from __future__ import annotations

def my_function(data: str | None):
    pass

"""
University Website Scraper for RAG Data Acquisition
=====================================================
Crawls a university site starting from a seed URL,
extracts clean text content, and saves results to JSON.

Install dependencies:
    pip install requests beautifulsoup4 trafilatura lxml
"""

import json
import time
import re
from urllib.parse import urljoin, urlparse
from collections import deque

import requests
from bs4 import BeautifulSoup
import trafilatura


# ── Configuration ────────────────────────────────────────────────────────────

SEED_URL      = "https://datascience.uchicago.edu/education/masters-programs/ms-in-applied-data-science/"   # ← change this
MAX_PAGES     = 600          # safety cap while testing; raise for full crawl
CRAWL_DELAY   = 1.0         # seconds between requests (be polite)
OUTPUT_FILE = r"/Users/anmolmadan/Documents/University of Chicago/Gen AI/scraped_pages.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; UniRAGBot/1.0; "
        "+https://your-project-url/bot-info)"          # identify your bot
    )
}

# Only follow links whose path starts with these prefixes (None = all pages)
ALLOWED_PATH_PREFIXES =  ["/education/masters-programs"]   # e.g. ["/academics", "/research", "/about"]

# Skip URLs matching these patterns
SKIP_PATTERNS = [
    r"\.(pdf|docx?|xlsx?|pptx?|zip|png|jpe?g|gif|svg|mp4|mp3)$",
    r"/login", r"/logout", r"/search", r"/calendar", r"#",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def is_same_domain(url: str, base: str) -> bool:
    return urlparse(url).netloc == urlparse(base).netloc


def should_skip(url: str) -> bool:
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    if ALLOWED_PATH_PREFIXES:
        path = urlparse(url).path
        return not any(path.startswith(p) for p in ALLOWED_PATH_PREFIXES)
    return False


def fetch_page(url: str, session: requests.Session):
    """Fetch a URL; return (response | None, status_code | None)."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp, resp.status_code
    except requests.exceptions.HTTPError as e:
        print(f"    ✗ HTTP error {e.response.status_code} — {url}")
        return None, e.response.status_code
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Request failed — {url} ({e})")
        return None, None


def extract_links(html: str, base_url: str) -> list[str]:
    """Pull all same-domain href links from a page."""
    soup = BeautifulSoup(html, "lxml")
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        absolute = urljoin(base_url, href)
        # Normalise: drop fragment, trailing slash
        absolute = absolute.split("#")[0].rstrip("/")
        if is_same_domain(absolute, base_url) and not should_skip(absolute):
            links.append(absolute)
    return list(set(links))


def extract_content(html: str, url: str) -> dict | None:
    """
    Use trafilatura for main-content extraction.
    Falls back to BeautifulSoup <main>/<article> if trafilatura returns nothing.
    """
    # --- trafilatura (primary) ---
    text = trafilatura.extract(
        html,
        include_tables=True,
        include_links=False,
        no_fallback=False,
    )

    # --- BeautifulSoup fallback ---
    if not text:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        container = soup.find("main") or soup.find("article") or soup.body
        text = container.get_text(separator="\n", strip=True) if container else ""

    if not text or len(text.strip()) < 100:   # ignore near-empty pages
        return None

    soup = BeautifulSoup(html, "lxml")
    title = soup.title.string.strip() if soup.title else ""

    return {
        "url":        url,
        "title":      title,
        "text":       text.strip(),
        "char_count": len(text.strip()),
    }


# ── Diagnostic print helpers ──────────────────────────────────────────────────

def print_banner(msg: str):
    print(f"\n{'═'*60}\n  {msg}\n{'═'*60}")

def print_page_result(page: dict):
    preview = page["text"][:200].replace("\n", " ")
    print(f"    Title : {page['title'][:70]}")
    print(f"    Chars : {page['char_count']:,}")
    print(f"    Preview: {preview}…")


# ── Main crawler ──────────────────────────────────────────────────────────────

def crawl(seed_url: str) -> list[dict]:
    print_banner(f"Starting crawl from: {seed_url}")

    # --- Check robots.txt ---
    robots_url = urljoin(seed_url, "/robots.txt")
    session = requests.Session()
    r, _ = fetch_page(robots_url, session)
    if r:
        print(f"✔ robots.txt found ({len(r.text)} chars) — review before large crawls")
        print(r.text[:400])
    else:
        print("⚠ robots.txt not found or inaccessible")

    # --- Check sitemap ---
    sitemap_url = urljoin(seed_url, "/sitemap.xml")
    r, code = fetch_page(sitemap_url, session)
    if r:
        print(f"\n✔ sitemap.xml found ({len(r.text)} chars) — could be used to seed URLs")
    else:
        print(f"\n⚠ sitemap.xml not found (status {code})")

    visited   = set()
    queue     = deque([seed_url.rstrip("/")])
    results   = []
    page_num  = 0

    print(f"\n{'─'*60}")
    print(f"  Crawling up to {MAX_PAGES} pages  |  delay: {CRAWL_DELAY}s")
    print(f"{'─'*60}\n")

    while queue and page_num < MAX_PAGES:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        page_num += 1

        print(f"[{page_num:>3}/{MAX_PAGES}] Fetching: {url}")

        resp, status = fetch_page(url, session)
        if resp is None:
            continue

        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            print(f"    ↷ Skipping non-HTML content-type: {content_type}")
            continue

        html = resp.text

        # Extract content
        page_data = extract_content(html, url)
        if page_data:
            results.append(page_data)
            print_page_result(page_data)
        else:
            print("    ↷ Skipped — insufficient text content")

        # Discover new links
        new_links = extract_links(html, seed_url)
        added = 0
        for link in new_links:
            if link not in visited and link not in queue:
                queue.append(link)
                added += 1
        print(f"    Links discovered: {len(new_links)}  |  new in queue: {added}  |  queue size: {len(queue)}\n")

        time.sleep(CRAWL_DELAY)

    # ── Summary ──────────────────────────────────────────────────────────────
    print_banner("Crawl Complete — Summary")
    print(f"  Pages attempted : {page_num}")
    print(f"  Pages saved     : {len(results)}")
    print(f"  Pages skipped   : {page_num - len(results)}")
    if results:
        total_chars = sum(p["char_count"] for p in results)
        avg_chars   = total_chars // len(results)
        print(f"  Total chars     : {total_chars:,}")
        print(f"  Avg chars/page  : {avg_chars:,}")
        print(f"\n  Top 5 pages by content length:")
        for p in sorted(results, key=lambda x: x["char_count"], reverse=True)[:5]:
            print(f"    {p['char_count']:>7,} chars  {p['url']}")

    return results


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pages = crawl(SEED_URL)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    print(f"\n✔ Saved {len(pages)} pages → {OUTPUT_FILE}")

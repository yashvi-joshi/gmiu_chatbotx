import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import json
import time

START_URLS = [
    "https://gmiu.edu.in/gmiu/website/",
    "https://admission.gmiu.edu.in/"
]

ALLOWED_DOMAINS = {
    "gmiu.edu.in",
    "www.gmiu.edu.in",
    "admission.gmiu.edu.in"
}

MAX_PAGES = 100

visited = set()
queue = deque(START_URLS)
pages = []

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; GMIUStudentAssistant/1.0)"
}


def clean_url(url):
    parsed = urlparse(url)
    return parsed._replace(fragment="", query="").geturl().rstrip("/")


while queue and len(pages) < MAX_PAGES:
    url = clean_url(queue.popleft())

    if url in visited:
        continue

    parsed = urlparse(url)

    if parsed.netloc not in ALLOWED_DOMAINS:
        continue

    if not parsed.scheme.startswith("http"):
        continue

    visited.add(url)

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            print("Skipped:", response.status_code, url)
            continue

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type:
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup([
            "script", "style", "nav", "footer", "header",
            "noscript", "svg"
        ]):
            element.decompose()

        title = soup.title.get_text(" ", strip=True) if soup.title else ""

        text = soup.get_text(" ", strip=True)
        text = " ".join(text.split())

        if len(text) > 100:
            pages.append({
                "title": title,
                "url": url,
                "content": text
            })

            print(f"Collected {len(pages)}: {title}")

        for link in soup.find_all("a", href=True):
            next_url = clean_url(urljoin(url, link["href"]))
            next_parsed = urlparse(next_url)

            if (
                next_parsed.netloc in ALLOWED_DOMAINS
                and next_url not in visited
                and next_parsed.path
                and not next_parsed.path.lower().endswith(
                    (".pdf", ".jpg", ".jpeg", ".png", ".zip")
                )
            ):
                queue.append(next_url)

        time.sleep(0.3)

    except requests.RequestException as error:
        print("Error:", url, error)


with open("gmiu_knowledge.json", "w", encoding="utf-8") as file:
    json.dump(pages, file, ensure_ascii=False, indent=2)

print("\nCollection finished!")
print("Pages collected:", len(pages))
print("Saved to gmiu_knowledge.json")

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

FILE = Path("gmiu_knowledge.json")

URLS = [
    "https://gmiu.edu.in/gmiu/website/admission/courses_offered.php",
    "https://www.gmiu.edu.in/gmiu/website/admission/scholarships.php",
    "https://gmiu.edu.in/gmiu/website/admission/how-to-apply.php",
    "https://gmiu.edu.in/gmiu/website/campus/FAQ.php",
    "https://gmiu.edu.in/gmiu/website/admission/admission_brochure.php",
    "https://gmiu.edu.in/gmiu/website/public_self_disclosure.php",
    "https://admission.gmiu.edu.in/all-documents",
    "https://admission.gmiu.edu.in/faq",
]

if FILE.exists():
    pages = json.loads(FILE.read_text(encoding="utf-8"))
else:
    pages = []

existing_urls = {p.get("url", "").rstrip("/") for p in pages}

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; GMIUStudentAssistant/1.0)"
}

added = 0

for url in URLS:
    if url.rstrip("/") in existing_urls:
        print("Already collected:", url)
        continue

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        title = soup.title.get_text(" ", strip=True) if soup.title else url
        content = soup.get_text(" ", strip=True)

        if len(content) < 100:
            print("Little readable content found:", url)
            continue

        pages.append({
            "title": title,
            "url": url,
            "content": content
        })

        existing_urls.add(url.rstrip("/"))
        added += 1
        print("Added:", title)

    except Exception as error:
        print("Could not collect:", url)
        print("Reason:", error)

FILE.write_text(
    json.dumps(pages, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("\nFinished!")
print("New pages added:", added)
print("Total pages now:", len(pages))
print("Saved to:", FILE)

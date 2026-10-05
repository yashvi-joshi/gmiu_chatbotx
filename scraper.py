import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://gmiu.edu.in/gmiu/website/home/circular.php"


def scrape_circulars():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    circulars = []

    for row in soup.find_all("tr"):
        columns = row.find_all(["td", "th"])

        if len(columns) >= 3:
            title = columns[1].get_text(" ", strip=True)
            date = columns[2].get_text(" ", strip=True)

            if title.lower() == "title" and date.lower() == "date":
                continue

            link = ""

            for a in row.find_all("a", href=True):
                link = urljoin(URL, a["href"])
                break

            circulars.append({
                "title": title,
                "date": date,
                "link": link
            })

    return circulars


if __name__ == "__main__":
    data = scrape_circulars()

    for circular in data:
        print(circular)

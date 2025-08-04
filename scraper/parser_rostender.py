import asyncio, httpx
from bs4 import BeautifulSoup
stored_tenders = None

semaphore = asyncio.Semaphore(10)

async def fetch_page_async(client: httpx.AsyncClient, url: str):
    async with semaphore:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.text
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Нет ответа от {url}: {e}")
            return None


async def get_tender_urls_from_page(client: httpx.AsyncClient, page_num: int) -> list[str]:
    url = f"https://rostender.info/extsearch?page={page_num}"
    html = await fetch_page_async(client, url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    links = soup.find_all("a", class_="url")

    urls = []
    for link in links:
        href = link.get("href")
        urls.append(href)
    return urls

def get_tender_number(soup: BeautifulSoup) -> str:
    div = soup.find("div", class_="tender-info-header-number")
    if div:
        div_text = div.get_text(strip=True)
        return div_text[8:] # можно сделать так, потому что там всегда есть слово "Тендер: "
    return ''

def get_tender_name(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1", {"data-id": "name"})
    if h1:
        h1_text = h1.get_text(strip=True)
        return h1_text[8:]  # можно сделать так, потому что там всегда есть слово "Тендер: "
    return "Название не найдено"


def get_tender_price(soup: BeautifulSoup) -> str:
    price_label = soup.find(string="Начальная цена")
    if price_label:
        parent = price_label.find_parent("div")
        if parent:
            price_tag = parent.find("strong") or parent.find("span", class_="tender-body__text")
            if price_tag:
                return price_tag.get_text(strip=True)
    return "Цена не найдена"


def get_tender_location(soup: BeautifulSoup) -> str:
    city, loc = '', ''
    city_tag = soup.find("span", class_="tender-info__text")
    if city_tag:
        city = city_tag.get_text(strip=True)
    location_tag = soup.find("a", class_="tender-body__text gray-text-small")
    if location_tag:
        loc = location_tag.get_text(strip=True)
    return city + ', ' + loc

def get_tender_end_date(soup: BeautifulSoup) -> str:
    date = soup.find("span", class_="black")
    time = soup.find("span", class_="tender__countdown-container")
    date_text, time_text = '', ''
    if date:
        date_text = date.get_text(strip=True)
    if time:
        time_text = time.get_text(strip=True)
    return date_text + ' ' + time_text


async def get_tender_info(client: httpx.AsyncClient, url: str) -> dict[str, str]:
    html = await fetch_page_async(client, url)
    if not html:
        return {"url": url, "name": "Ошибка загрузки", "price": "-", "location": "-"}

    soup = BeautifulSoup(html, "lxml")

    return {
        "url": url,
        "number": get_tender_number(soup),
        "name": get_tender_name(soup),
        "price": get_tender_price(soup),
        "location": get_tender_location(soup),
        "end_date": get_tender_end_date(soup),
    }



async def scrape_tenders(max_tenders: int = 100) -> list[dict[str, str]]:
    async with httpx.AsyncClient(headers={
        "User-Agent": "Mozilla/5.0 (compatible; TenderBot/0.1)"
    }) as client:
        urls = []
        page = 1

        while len(urls) < max_tenders:
            batch = await get_tender_urls_from_page(client, page)
            if not batch:
                print(f"Не нашел больше тендеров на странице {page}, остановка.")
                break
            urls.extend(batch)
            if len(urls) >= max_tenders:
                break
            page += 1

        urls = urls[:max_tenders]
        print(f"Найдено {len(urls)} тендеров. Достаем детали...")

        tasks = [get_tender_info(client, url) for url in urls]
        tenders = await asyncio.gather(*tasks)

        return tenders

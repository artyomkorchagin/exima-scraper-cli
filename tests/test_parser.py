import pytest
from bs4 import BeautifulSoup
import httpx
import respx

from scrapper.parser_rostender import (
    get_tender_price,
    get_tender_info,
    get_tender_urls_from_page,
    scrape_tenders
)

filepath = './tests/test.html'

@pytest.fixture
def soup():
    def _soup(html):
        return BeautifulSoup(html, "lxml")
    return _soup


def test_get_tender_price(soup):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    bs = soup(html_content)
    assert get_tender_price(bs) == "1 395 132 ₽"


def test_get_tender_price_with_spaces(soup):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    bs = soup(html_content)
    assert get_tender_price(bs) == "1 395 132 ₽"


@pytest.mark.asyncio
async def test_get_tender_info_success(soup):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    bs = soup(html_content)

    class MockResponse:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            pass

    class MockClient:
        async def get(self, url, timeout=None):
            return MockResponse(html_content)

    client = MockClient()
    result = await get_tender_info(client, "https://rostender.info/tender/123")

    assert result["price"] == "1 395 132 ₽"
    assert result["name"] == "Поставка изделий медицинского назначения"
    assert result["location"] == "Респ. Чеченская, Чеченская республика"
    assert result["end_date"] == "12.08.2025 09:00"


@pytest.mark.asyncio
@respx.mock
async def test_get_tender_urls_from_page():
    respx.get("https://rostender.info/extsearch?page=1").respond(
        status_code=200,
        content='''
        <a href="https://rostender.info/tender/123" class="url"></a>
        <a href="https://rostender.info/tender/456" class="url"></a>
        '''
    )

    async with httpx.AsyncClient() as client:
        urls = await get_tender_urls_from_page(client, 1)

    assert urls == [
        "https://rostender.info/tender/123",
        "https://rostender.info/tender/456"
    ]


@pytest.mark.asyncio
@respx.mock
async def test_scrape_tenders():
    respx.get("https://rostender.info/extsearch?page=1").respond(
        status_code=200,
        content='''
        <a href="https://rostender.info/tender/123" class="url"></a>
        '''
    )
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    respx.get("https://rostender.info/tender/123").respond(
        status_code=200,
        content=html_content
    )

    tenders = await scrape_tenders(max_tenders=1)
    assert len(tenders) == 1
    assert tenders[0]["price"] == "1 395 132 ₽"
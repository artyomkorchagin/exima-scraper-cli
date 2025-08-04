import asyncio, click, uvicorn, csv
from pathlib import Path
from scrapper.parser_rostender import scrape_tenders
from scrapper.api import get_app
from scrapper.api import get_tenders
from scrapper.definitions import SAVE_DIR

def save_to_csv(tenders: list[dict[str, str]], filename: str):
    keys = ["number", "name", "price", "location", "end_date", "url"]
    filepath = Path(SAVE_DIR, filename)

    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(tenders)
    print(f"Сохранено {len(tenders)} тендеров в {filename}")

@click.command()
@click.option(
    "--max",
    "tenders",
    default=20,
    show_default=True,
    type=click.IntRange(1, 200),
    help="Количество тендеров"
)
@click.option(
    "--output",
    default="tenders.csv",
    type=click.Path(),
    help="Файл для сохранения результатов (CSV)"
)
def cli(tenders: int, output: str):
    print(SAVE_DIR)
    click.echo(f"Парсинг {tenders} тендеров...")
    stored_tenders = asyncio.run(scrape_tenders(max_tenders=tenders))

    get_tenders(stored_tenders)

    save_to_csv(stored_tenders, output)
    uvicorn.run(get_app(), host="0.0.0.0", port=8000)

def main():
    cli()

if __name__ == "__main__":
    main()

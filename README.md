# Парсер тендеров с rostender.info

Парсит тендеры с [rostender.info/extsearch](https://rostender.info/extsearch), извлекает ключевые данные и сохраняет в CSV.

---

## Зависимости
- httpx
- beautifulsoup4
- lxml
- fastapi
- uvicorn
- click
- pytest
- respx 

## Установка

```bash
git clone https://github.com/artyomkorchagin/exima-scrapper-cli.git
cd exima-scraper-cli
pip install -e .
```

## Использование

```bash
cd scraper
python main.py --max 10 --output tenders.csv
```

- --max — количество тендеров (по умолчанию 100)
- --output — путь к файлу CSV (директории создаются автоматически)

## Тесты
```bash
pytest tests/ -v
```

## FastAPI

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/` | Перенаправляет на /status |
| `GET` | `/status` | Проверка работоспособности API |
| `GET` | `/tenders` | Возвращает запарсенные данные |

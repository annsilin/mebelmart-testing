# Фреймворк автоматизированного тестирования Мебельмарт

Фреймворк GUI-тестирования для сайта [mebelmart-saratov.ru](https://mebelmart-saratov.ru/myagkaya_mebel_v_saratove/divanyi_v_saratove) на основе Python, Playwright и Allure.

---

## Содержание

- [Структура проекта](#структура-проекта)
- [Технологии](#технологии)
- [Тест-сценарии](#тест-сценарии)
- [Локальная установка](#локальная-установка)
- [Запуск тестов локально](#запуск-тестов-локально)
- [Docker + Jenkins](#docker-инфраструктура--jenkins-cicd)


---

## Структура проекта

```
mebelmart-testing/
├── config/
│   └── config.py                  # URL, таймауты, настройки браузера
├── docker-setup/
│   ├── docker-compose.yml         # Сервисы Jenkins и Allure
│   ├── jenkins/
│   │   ├── Dockerfile             # Jenkins с Docker CLI
│   │   ├── docker-entrypoint.sh  # Исправление прав Docker-сокета
│   │   └── plugins.txt           # Список плагинов Jenkins
│   └── tests/
│       ├── Dockerfile             # Образ для запуска тестов (Playwright)
│       └── entrypoint.sh         # Запуск Xvfb и pytest
├── pages/
│   ├── base_page.py              # Базовый Page Object (навигация, скролл, ожидания)
│   ├── couches_catalog_page.py   # Каталог: фильтр, карточки, избранное
│   ├── product_page.py           # Страница товара: характеристики, корзина
│   ├── cart_page.py              # Корзина
│   ├── favorites_page.py         # Избранное
│   └── search_results_page.py    # Результаты поиска
├── tests/
│   ├── test_price_filter.py      # Сценарий 2.1 — фильтр по цене через слайдер
│   ├── test_product_details.py   # Сценарий 2.2 — характеристики товара
│   ├── test_add_to_favorites.py  # Сценарий 2.3 — добавление в избранное
│   ├── test_search.py            # Сценарий 2.4 — поиск по названию
│   └── test_cart.py              # Сценарий 2.5 — добавление в корзину
├── utils/
│   └── screenshot_utils.py       # Захват скриншота и прикрепление к Allure
├── conftest.py                    # Фикстуры, обработчик диалогов, хук скриншота
├── pytest.ini                     # Конфигурация pytest
└── requirements.txt               # Зависимости Python
```

---

## Технологии

| Категория | Инструмент |
|---|---|
| Язык | Python 3.10+ |
| Автоматизация браузера | Playwright (`pytest-playwright`) |
| Тестовый фреймворк | pytest |
| Репортинг | Allure (`allure-pytest`) |
| Браузеры | Chromium, Firefox |
| CI/CD | Jenkins |
| Контейнеризация | Docker + Docker Compose |
| Логирование | Python `logging` (stdlib) |

---

## Тест-сценарии

| Файл | Сценарий | Описание |
|---|---|---|
| `test_price_filter.py` | 2.1 | Фильтрация по цене через слайдер (10 000–15 000 ₽), проверка наличия дивана «Лотос» в результатах |
| `test_product_details.py` | 2.2 | Клик на «Чебурашку» в каталоге, открытие страницы товара, переход на вкладку «Характеристики», сравнение размеров с карточкой каталога |
| `test_add_to_favorites.py` | 2.3 | Клик на иконку избранного у первого товара, проверка активного состояния иконки, переход в избранное, проверка наличия товара |
| `test_search.py` | 2.4 | Ввод «Чебурашка» в строку поиска, нажатие Enter, проверка что первый результат содержит искомое слово |
| `test_cart.py` | 2.5 | Открытие первого товара, клик «В корзину», переход в корзину, проверка товара и цены |

---

## Локальная установка

### Требования

- Python 3.10+
- Git

### Установка

```bash
git clone https://github.com/<your-username>/mebelmart-testing.git
cd mebelmart-testing

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
playwright install
```

---

## Запуск тестов локально

### Все тесты (headless Chromium)

```bash
pytest
```

### Выбор браузера

```bash
pytest --browser=chromium
pytest --browser=firefox
```

### Видимый режим

```bash
pytest --headed
```

### Один конкретный тест

```bash
pytest tests/test_price_filter.py -v
pytest -k test_cart -v
```

### Генерация и просмотр Allure-отчёта

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

---

## Docker-инфраструктура + Jenkins CI/CD

[docker-setup/README.md](docker-setup/README.md)
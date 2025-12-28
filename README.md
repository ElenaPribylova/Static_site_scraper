# Static_site_scraper
Python web scraper for glavsnab.net
Парсит одну категорию товаров с сайта glavsnab.net и сохраняет данные в glavsnab.csv. Извлекает артикул, название, ссылку на товар и цену.
Для запуска скопируйте URL нужной страницы  и количестко товаров в этой категории
пример: parser(url="https://glavsnab.net/stroymateriali/gipsokarton.html?limit=100", max_item=1132)
Этика: таймаут запроса: 10 сек, пауза между запросами: 1 сек (time.sleep(1)).

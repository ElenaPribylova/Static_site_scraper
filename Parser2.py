import requests
from bs4 import BeautifulSoup
import csv
from dataclasses import dataclass
import time
from urllib3.util import url
@dataclass
class product:
    sku: str
    name: str
    link: str
    price: str

def parser(url: str, max_item: int):
    create_csv()
    page = 1  # счетчик, с какой страницы должен начинаться отсчет
    count_item = 0  # счетчик просмотренных ранее карточек
    list_product = []
    while count_item < max_item:
        page_url = f"{url}&p={page}"  # формируем URL для текущей страницы

        try:
            res = requests.get(page_url, timeout=10)
            if res.status_code != 200:
                print(f"Ошибка {res.status_code} на странице {page_url}")
                page += 1
                time.sleep(1)
                continue
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса на странице {page}: {e}")
            page += 1
            time.sleep(1)
            continue
        soup = BeautifulSoup(res.text, "lxml")
        products = soup.find_all("div", class_="product-card")
        # Если товаров нет — завершаем
        if not products:
            print(f"Страница {page}: товаров не найдено. Завершаем.")
            break

        for item in products:
            if count_item >= max_item: #если достигается предел карточек
                break # цикл завершается по достижении предела количества карточек
            count_item += 1 #В цикле увеличиваем счетчик на 1 страницу

            name = item.get("data-product-name", "Не указано") # извлекаем имя
            sku_elem = item.find("span", class_="product-card__key") #извлекаем артикул
            sku = sku_elem.text.strip() if sku_elem else "Не указано"
            name_elem = item.find("meta", itemprop="name")
            link = name_elem.find_next().get("href") if name_elem else "#" #извлекаем ссылку
            price_elem = item.find("span", itemprop="price") # извлекаем цену
            price = price_elem.get("content", "По запросу") if price_elem else "По запросу"
            list_product.append(product(sku=sku, name=name, link=link, price=price))

        page += 1
        time.sleep(1)

    write_csv(list_product)


def create_csv():
    with open('glavsnab.csv', mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sku', 'name', 'link', 'price'])

def write_csv(products: list[product]):
    with open('glavsnab.csv', mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for product in products:
            writer.writerow([product.sku, product.name, product.link, product.price])




if __name__ == '__main__':
    parser(url="https://glavsnab.net/stroymateriali/gipsokarton.html?limit=100", max_item=1132)


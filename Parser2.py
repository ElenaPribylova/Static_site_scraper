import requests
from bs4 import BeautifulSoup
import csv
from dataclasses import dataclass
import time
import statistics
from collections import Counter
import matplotlib.pyplot as plt


@dataclass
class product:
    sku: str
    name: str
    link: str
    price: str


def parser(url: str, max_item: int):
    create_csv()
    page = 1
    count_item = 0
    list_product = []

    while count_item < max_item:
        page_url = f"{url}&p={page}"
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

        if not products:
            print(f"Страница {page}: товаров не найдено. Завершаем.")
            break

        for item in products:
            if count_item >= max_item:
                break
            count_item += 1

            name = item.get("data-product-name", "Не указано")
            sku_elem = item.find("span", class_="product-card__key")
            sku = sku_elem.text.strip() if sku_elem else "Не указано"
            name_elem = item.find("meta", itemprop="name")
            link = name_elem.find_next().get("href") if name_elem else "#"
            price_elem = item.find("span", itemprop="price")
            price = price_elem.get("content", "По запросу") if price_elem else "По запросу"

            list_product.append(product(sku=sku, name=name, link=link, price=price))

        page += 1
        time.sleep(1)

    write_csv(list_product)
    analyze(list_product)
    return list_product


def create_csv():
    with open('glavsnab.csv', mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sku', 'name', 'link', 'price'])


def write_csv(products: list[product]):
    with open('glavsnab.csv', mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for product in products:
            writer.writerow([product.sku, product.name, product.link, product.price])


def analyze(products: list[product]):
    # фильтр валидных цен
    prices = []
    for p in products:
        try:
            prices.append(float(p.price))
        except:
            pass

    if not prices:
        print("Нет данных для анализа")
        return

    # базовая статистика
    stats = calc_stats(prices)
    print_stats(stats)

    # детекция аномалий
    anomalies = detect_anomalies(products, prices)
    print_anomalies(anomalies)

    # частотный анализ названий
    freq = word_frequency(products)
    print_frequency(freq)

    # визуализация
    visualize(prices, stats)

    # сохранение отчета
    save_report(stats, anomalies, freq)


def calc_stats(prices: list[float]) -> dict:
    # расчет основных метрик
    return {
        'min': min(prices),
        'max': max(prices),
        'mean': statistics.mean(prices),
        'median': statistics.median(prices),
        'stdev': statistics.stdev(prices) if len(prices) > 1 else 0,
        'count': len(prices),
        'q1': statistics.quantiles(prices, n=4)[0] if len(prices) >= 4 else min(prices),
        'q3': statistics.quantiles(prices, n=4)[2] if len(prices) >= 4 else max(prices)
    }


def detect_anomalies(products: list[product], prices: list[float]) -> dict:
    # метод межквартильного размаха (IQR)
    if len(prices) < 4:
        return {'low': [], 'high': []}

    q1 = statistics.quantiles(prices, n=4)[0]
    q3 = statistics.quantiles(prices, n=4)[2]
    iqr = q3 - q1
    low_bound = q1 - 1.5 * iqr
    high_bound = q3 + 1.5 * iqr

    low_anomalies = []
    high_anomalies = []

    for p in products:
        try:
            price = float(p.price)
            if price < low_bound:
                low_anomalies.append((p.name, price))
            elif price > high_bound:
                high_anomalies.append((p.name, price))
        except:
            pass

    return {'low': low_anomalies, 'high': high_anomalies}


def word_frequency(products: list[product]) -> dict:
    # топ слов в названиях
    words = []
    stop_words = {'и', 'в', 'на', 'с', 'для', 'по', 'из', 'от', 'до'}

    for p in products:
        tokens = p.name.lower().split()
        words.extend([w for w in tokens if len(w) > 2 and w not in stop_words])

    counter = Counter(words)
    return dict(counter.most_common(10))


def print_stats(stats: dict):
    print(
        f"\nТоваров: {stats['count']} | Мин: {stats['min']:.0f}₽ | Макс: {stats['max']:.0f}₽ | Средняя: {stats['mean']:.0f}₽ | Медиана: {stats['median']:.0f}₽")


def print_anomalies(anomalies: dict):
    low_cnt = len(anomalies['low'])
    high_cnt = len(anomalies['high'])
    if low_cnt > 0 or high_cnt > 0:
        print(f"Аномалии: низкие цены ({low_cnt}), высокие ({high_cnt})")


def print_frequency(freq: dict):
    top5 = list(freq.items())[:5]
    words = ', '.join([f"{w}({c})" for w, c in top5])
    print(f"Топ слов: {words}")


def visualize(prices: list[float], stats: dict):
    # простая гистограмма
    plt.figure(figsize=(10, 6))
    plt.hist(prices, bins=25, edgecolor='black', alpha=0.7, color='steelblue')
    plt.axvline(stats['mean'], color='red', linestyle='--', linewidth=2, label=f"среднее {stats['mean']:.0f}₽")
    plt.axvline(stats['median'], color='green', linestyle='--', linewidth=2, label=f"медиана {stats['median']:.0f}₽")
    plt.xlabel('Цена, руб', fontsize=12)
    plt.ylabel('Количество товаров', fontsize=12)
    plt.title('Распределение цен', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig('price_analysis.png', dpi=120)
    print("График: price_analysis.png")


def save_report(stats: dict, anomalies: dict, freq: dict):
    # текстовый отчет
    with open('analytics_report.txt', 'w', encoding='utf-8') as f:
        f.write("АНАЛИТИЧЕСКИЙ ОТЧЕТ\n\n")

        f.write("Статистика цен:\n")
        f.write(f"Товаров: {stats['count']}\n")
        f.write(f"Диапазон: {stats['min']:.0f} - {stats['max']:.0f} руб\n")
        f.write(f"Средняя: {stats['mean']:.0f} руб\n")
        f.write(f"Медиана: {stats['median']:.0f} руб\n")
        f.write(f"Отклонение: {stats['stdev']:.0f} руб\n\n")

        f.write("Аномалии:\n")
        f.write(f"Низкие цены: {len(anomalies['low'])}\n")
        f.write(f"Высокие цены: {len(anomalies['high'])}\n\n")

        if anomalies['low']:
            f.write("Примеры низких цен:\n")
            for name, price in anomalies['low'][:3]:
                f.write(f"  {price:.0f}₽ - {name}\n")
            f.write("\n")

        if anomalies['high']:
            f.write("Примеры высоких цен:\n")
            for name, price in anomalies['high'][:3]:
                f.write(f"  {price:.0f}₽ - {name}\n")
            f.write("\n")

        f.write("Топ-10 слов в названиях:\n")
        for word, count in freq.items():
            f.write(f"{word}: {count}\n")

    print("Отчет: analytics_report.txt\n")


if __name__ == '__main__':
    parser(url="https://glavsnab.net/stroymateriali/gipsokarton.html?limit=100", max_item=1132)

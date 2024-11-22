import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import pandas as pd
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

START_YEAR = 1920


def load_wines(file_path):
    wines_xlsx = pd.read_excel(
        file_path,
        na_values=['N/A', 'NA'],
        keep_default_na=False
    )
    wines = wines_xlsx.to_dict(orient='records')
    grouped_wines = defaultdict(list)
    for wine in wines:
        grouped_wines[wine['Категория']].append(wine)
    return grouped_wines


def pluralize_years(years):
    if 11 <= years % 100 <= 19:
        return f"{years} лет"
    elif years % 10 == 1:
        return f"{years} год"
    elif 2 <= years % 10 <= 4:
        return f"{years} года"
    else:
        return f"{years} лет"


def render_template(template_name, context):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск веб-сервера и отображение данных о вине.")

    parser.add_argument('--data', type=str, default=os.getenv('WINE_DATA_PATH', 'wine.xlsx'),
                        help="Путь к файлу с данными о вине (по умолчанию 'wine.xlsx').")

    parser.add_argument('--template', type=str, default=os.getenv('TEMPLATE_PATH', 'template.html'),
                        help="Путь к файлу шаблона (по умолчанию 'template.html').")

    args = parser.parse_args()

    grouped_wines = load_wines(args.data)
    total_years = pluralize_years(datetime.now().year - START_YEAR)

    rendered_page = render_template(args.template, {
        'grouped_wines': grouped_wines,
        'total_years': total_years
    })

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()
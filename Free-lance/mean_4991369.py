# TODO: разделить на отдельны функции сохранение страниц на компьютере, отдельно фукнцию по парсингу и сохранению в таблицы

# https://www.fl.ru/projects/4991369/sparsit-dannyie-s-sayta.html
# 26.05.2022
# Спарсить с сайта модели техники и фото к ним.
# сайт – servisniy-center-bosch.ru
# Там 3 типа техники. стиралки, сушилки, посудомойки.
#
# Спарсить. типы техники – бренд – модель – фото
# 4 таблицы в БД. структура БД.
# 1. (type) Типы техники (id, name)
# 2. (brand) Бренд (id, type_id, name)
# 3. (model) Название модели (id, brand_id, type_id, name)
# 4. (photos) Фото (id, name, model_id, brand_id)
#
# Файлы с картинками сразу переименовать и хранить в бд с таким названием,
# транслитом (маленькие буквы) пример:
# 15567-bosch-serie-6-wat28321.jpg
# 15567 – это id картинки в базе в таблице photos.
# все файлы картинок будут в одной папке.

# импортируем необходимые модули
import csv
from bs4 import BeautifulSoup
import requests
import json
from time import sleep
import random
import os
import sys
import logging
import urllib.request
from PIL import Image
import sqlalchemy
import pandas as pd


# подключим логгирование
logger = logging.getLogger(__name__)
logging.basicConfig(filename="data/mylog.log", filemode='w', level=logging.INFO)
url = "https://servisniy-center-bosch.ru/"

headers = {
    'Accept':'*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.143 YaBrowser/22.5.0.1816 Yowser/2.5 Safari/537.36'
}
logging.basicConfig(level=logging.INFO)

def title_csv():
    '''
        Function create empty table with columns and headers
        1. (type) Типы техники (id, name)
        2. (brand) Бренд (id, type_id, name)
        3. (model) Название модели (id, brand_id, type_id, name)
        4. (photos) Фото (id, name, model_id, brand_id)
    '''

    header_tables = {
                      'type':('id', 'name'),
                      'brand':('id', 'type_id', 'name'),
                      'model':('id', 'brand_id', 'type_id', 'name'),
                      'photos':('id', 'name', 'model_id', 'brand_id')
                    }
    for i in header_tables.keys():
        values = header_tables.get(i)
        with open('data/' + str(i) + '.csv', 'w', encoding='utf-8',
                  newline='') as f:

            writer = csv.writer(f, delimiter=";")

            writer.writerow(values)

def get_href():

    '''
    Функция проверят существование файла-образа html-страницы, если нет, то
    выполняет request, save result to file *.html.
    Сохраняет в файл *.json гиперссылки на другие страницы.

    :return:
    '''
    # проверим, возможно файл уже существует, тогде не нужно загружать

    file_index = f"data/index.html"

    if os.path.exists(file_index):
        print("Файл страницы сайта уже существует!")
        logger.info("Файл страницы сайта уже существует!")
        with open('data/index.html', 'r', encoding='utf-8') as file:
            scr = file.read()
    else:
        try:
            req = requests.get(url, headers=headers,
                               verify=False)  # запрос будет отправлен если файла нет
            scr = req.text

            with open('data/index.html', 'w', encoding='utf-8') as file:
                file.write(scr)
        except Exception as ex:
            print('Не удалось получить страницу, ' \
                  'программа будет остановлена.')
            sys.exit(1)
        # не стал использовать else, поскольку раз файла нет, а страницу не
        # получили, то нет смысла выполнять программу дальше

    with open('data/index.html', 'r', encoding='utf-8') as file:
        scr = file.read()

    # читаем файл страницы сайта

    soup = BeautifulSoup(scr, 'lxml')

    # получаем названия катеорий и гиппер-ссылки на соответствующие страницы,
    # созаем словарь
    card_link_href = soup.find_all(class_="card__link")

    card_link_dic = {}

    for item in card_link_href:
        category = item.find('img').get('alt')
        href = url + item.get('href')
        card_link_dic[category] = href

    print('Создали словарь с названиями катеорий и гиппер-ссылками на соответствующие страницы')

    # сохраняем категории и гипеер-ссылки в формат json, или перезапишем
    # файл, если тот уже есть
    with open ('data/card_link_dic.json', 'w', encoding='utf-8') as file:
        json.dump(card_link_dic, file, indent=4, ensure_ascii=False)

    print('Сохранили категории и гипеер-ссылки в формат json')

    return

def get_data():
    '''
    Функция извлекает названия брендов, моделей, скачивает картинки, сохраняет,
    данные в папки, таблицы.
    Модели техники находятся на страницах соответствующих категорий. По этому
    читаем созданный файл *.json, открываем href.

    :return:
    '''
    # комментируем ненужные строки
    # из сохраненного ранее файла json загужаем категории и гипер-ссылки
    with open('./data/card_link_dic.json', 'r', encoding='utf-8') as file:
        card_links = json.load(file)
    print('Выгрузили из файла json категории и гипер-ссылки')

    # посчитаем сколько всего категорий, сколько нужно всего итераций
    iter_count = int(len(card_links))

    # установим счетчик для текущей итерации
    count = 0
    count_id = 0
    print(f"Всего итераций: {iter_count}")

    # имена категорий и гиппер-ссылки хранятся в словаре итерируем словарь
    # при помощи констукции for ... in

    logger.info("Something relevant happened")
    for category_name, href in card_links.items():

        file_category_name = f'data/{count}_{category_name}'

        # проверяем существование файла, чтобы не обращаться к сайту, если
        # существует - пропустим else c try...except
        if os.path.exists(file_category_name + '.html'):

            print("Файл страницы сайта уже существует!")

            logger.info("Файл страницы сайта уже существует!")

        else:

            try:
                req = requests.get(url=href, headers=headers, verify=False)

                scr = req.text

                with open(file_category_name + '.html', 'w', encoding='utf-8',
                          newline='') as file:
                    file.write(scr)

            except Exception as ex:
                print('Не удалось получить страницу, ' \
                      'программа будет остановлена.')
                # continue, не знаю как заставить программу вернуться к for, а
                # не if, else, или try
                sys.exit(1)

        # берем html из файла
        with open(file_category_name + '.html', 'r', encoding='utf-8') as file:
            scr = file.read()

        # создаем объект BeautifulSoup
        soup = BeautifulSoup(scr, 'lxml')

        imag_link_href = soup.find_all(class_="card__image")

        get_imag_list = []  # словарь url на картинки

        type_id = count

        type_name = category_name

        for item in imag_link_href:
            # получаем url картинки
            url_get_imag = url + item.get('src')

            brand = 'Bosch'

            # выполним множественную замену в url,
            # заменим двойную косую на одинарную
            replace_values = {"ru//": "ru/",
                              'Ремонт стиральных машин':'Стиральная машина',
                              'Ремонт сушильных машин':'Сушильная машина',
                              'Ремонт посудомоечных машин':'Посудомоечная машина'}

            # вызовем функцию multiple_replace()
            url_get_imag = multiple_replace(url_get_imag, replace_values)

            # получаем название модели, пример, Serie 4 SMV 45IX00 R
            get_alt = item.get('alt').replace('Bosch ', '')

            # форматируем название модели, пример, wvd-24420,
            # serie-8-smv87tx01r
            ref_alt = get_alt.replace(' ', '-').lower()

            # генерируем название картинки по ТЗ, пример, 21-wtyh7781pl.jpg
            imag_name = str(count_id) + '-' + ref_alt + '.jpg'

            # получаем имя категории и заменяем ее, например,
            # Сушильная машина
            category_name = multiple_replace(category_name, replace_values)

            # передаем tuple в список
            get_imag_list.append((url_get_imag, get_alt, ref_alt, imag_name))

            # сохранить в csv
            with open(f'data/table.csv', 'a',
                      encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=";", )
                writer.writerow(
                    (
                        url_get_imag,
                        get_alt,
                        ref_alt,
                        imag_name
                    )
                )

            brand_id = 0
            brand_type_id = type_id
            brand_name = 'Bosch'
            model_id = count_id
            model_brand_id = brand_id
            model_type_id = type_id
            model_name = get_alt
            photos_id = count_id
            photos_name = imag_name
            photos_model_id = count_id
            photos_brand_id = brand_id

            with open(f'data/model.csv', 'a',
                      encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=";", )
                writer.writerow(
                    (
                        model_id,
                        model_brand_id,
                        model_type_id,
                        model_name
                    )
                )

            urllib.request.urlretrieve(url_get_imag, 'data/pic/' + imag_name)

            sleep(random.randrange(2, 4))  # рандомная пауза между
            # итерациями поскольк усбор данных происходит слишком быстро

            pillow('data/pic/', 'data/pic_jpg/', imag_name)

            with open(f'data/photos.csv', 'a',
                      encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=";", )
                writer.writerow(
                    (
                        photos_id,
                        photos_name,
                        photos_model_id,
                        photos_brand_id
                    )
                )
            count_id += 1

        with open(f'data/brand.csv', 'a',
                  encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=";", )
            writer.writerow(
                (
                    brand_id,
                    brand_type_id,
                    brand_name
                )
            )
        with open(f'data/type.csv', 'a',
                  encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=";", )
            writer.writerow(
                (
                    type_id,
                    category_name
                )
            )

        count += 1


def multiple_replace(target_str, replace_values):
    '''
    Функция выполняет множественную замену значения в строке
    по словарю и возвращает строку.
    :param target_str: str
    :param replace_values:
    :return: str
    '''

    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in replace_values.items():

    # меняем все target_str на подставляемое
        target_str = target_str.replace(i, j)

    return target_str

def pillow(path, targey_folder, imag_name):
    '''
    Function convert webp to jpg
    :return: file
    '''

    for filename in os.listdir(path):

        im = Image.open(path + filename).convert('RGB')

        im.save(targey_folder + filename[:-5] + '.jpg', 'jpeg')

def create_databases():

    try:

        conn = 'mysql+pymysql://root:j2706s0801@localhost:3307/'

        engine = sqlalchemy.create_engine(conn)

        engine.execute("commit")

        engine.execute("CREATE DATABASE scenter_bosch;")

    except Exception as ex:

        print('Невозможно подключиться к базе или она уже существует:\n', ex)

        conn = 'mysql+pymysql://root:j2706s0801@localhost:3307/scenter_bosch'

        engine = sqlalchemy.create_engine(conn)

        connect = engine.connect()

        print('БД подключена')

    for file_name in ['brand.csv', 'model.csv', 'photos.csv', 'type.csv']:

        df = pd.read_csv('data/' + file_name, index_col='id', delimiter=';' )

        df.to_sql(file_name[:-4], con=connect,
                  index=True,
                  index_label='id',
                  if_exists='replace',
                  dtype={"name": sqlalchemy.types.VARCHAR(length=255)})

def main():
    title_csv()
    get_href()
    get_data()
    pillow()
    create_databases()

if __name__ == '__main__':
    main()
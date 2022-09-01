# Программа для парсинга расходов и доходов из
# Отчета по дебетовой карте Сбербанка России
# -= автор Саенко Денис, 2022 год =-

# импортируем модули
import csv
from bs4 import BeautifulSoup

# открываем, читаем файл, сохраняем в переменную
with open('./data/Отчет по карте 0361 от 06.05.22.html',
          'r', encoding='utf-8') as file:
    scr = file.read()

# извлекаем html, для обработки разметки используем lxml
soup = BeautifulSoup(scr, 'lxml')

# сохраняем класс с таблицей в переменную
sic = soup.find_all(class_='trs_it')

# открываем файл на запись, устанавливаем разделитель
with open(f'data/data_.csv', 'w', encoding='utf-8',
          newline='') as f:
    writer = csv.writer(f, delimiter=";")

    # перебираем по элементам, находим в html, сохраняем в переменную
    for count, i in enumerate(sic, start=1):
        val = i.find(class_='trs_detail').find(class_='trs_val').text.strip() # код авторизации
        date_time = i.find(class_='idate').text # дата и время
        name = i.find('div', class_='trs_name').text.strip() # имя транзакции
        sum = i.find(class_='trs_sum').text.strip() # сумма транзакции
        icat = i.find(class_='trs_head').find(class_='trs_sic').find(class_='icat').text.strip() # категория транзакции
        country = i.find(class_='trs_detail trs-geo').find(class_='trs_val').find(class_='icoutry').text # страна

        # формируем файл csv построчно, заполняем значениями переменных
        writer.writerow((
            count,
            val,
            date_time,
            name,
            sum,
            icat,
            country,
        ))
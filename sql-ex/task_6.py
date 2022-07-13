'''
Задание: 6 (Serge I: 2002-10-28)
Для каждого производителя, выпускающего ПК-блокноты c объёмом жесткого диска
не менее 10 Гбайт, найти скорости таких ПК-блокнотов.
Вывод: производитель, скорость.

Схема БД состоит из четырех таблиц:
Product(maker, model, type)
PC(code, model, speed, ram, hd, cd, price)
Laptop(code, model, speed, ram, hd, price, screen)
Printer(code, model, color, type, price)
'''

SELECT Product.maker, Laptop.speed FROM Laptop
JOIN Product ON Product.model=Laptop.model
WHERE Laptop.hd >= 10;
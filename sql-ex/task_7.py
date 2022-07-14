'''
Схема БД состоит из четырех таблиц:
Product(maker, model, type)
PC(code, model, speed, ram, hd, cd, price)
Laptop(code, model, speed, ram, hd, price, screen)
Printer(code, model, color, type, price)

Задание: 7 (Serge I: 2002-11-02)
Найдите номера моделей и цены всех имеющихся в продаже продуктов (любого типа)
производителя B (латинская буква).
'''
SELECT DISTINCT Product.model, PC.price FROM Product
JOIN PC ON Product.model=PC.model WHERE maker='B'
UNION
SELECT DISTINCT Product.model, Laptop.price FROM Product
JOIN Laptop ON Product.model=Laptop.model WHERE maker='B'
UNION
SELECT DISTINCT Product.model, Printer.price FROM Product
JOIN Printer ON Product.model=Printer.model WHERE maker='B'
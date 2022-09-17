import os
import json
import psycopg2
import time

def ask_for_db_access():
    """
    Функция проверки доступа к БД

    Функция запрашивает данные для доступа к БД - имя базы и учетную запись
    администратора, - и проверяет их путем открытия соединения с БД. Попытка
    установления соединения производится до тех пор, пока пользователем не
    будут введены корректные данные - имя базы и учетная запись. Полученные
    данные сохраняются в json-файле и используются при следующем подключении.
    Информация об используемых учетных данных (кроме пароля) выводится на
    экран после успешного считывания настроек из json-файла. Для подключения
    с другими настройками следует отредактировать либо удалить json-файл.
    :return: открытое подключение
    """
    flag = False
    while flag == False:
        if os.path.exists('config.json'):
            config = open('config.json', 'r', encoding='cp1251')
            db_account = json.load(config)
            if db_account != {}:
                print()
                print(f"Будет использована БД {db_account['db_name']}, "
                      f"учетная запись - {db_account['login']}")
            else:
                print('Файл настроек существует, но не содержит данных')
                os.remove('config.json')
                print()
                continue
            config.close()

        else:
            db_account = {}
            config = open('config.json', 'w', encoding='cp1251')
            db_account['db_name'] = input('Введите название базы данных: ')
            db_account['login'] = input('Введите логин учетной записи базы '
                                        'данных: ')
            db_account['password'] = input('Введите пароль учетной записи '
                                           'базы данных: ')
            print()
            json.dump(db_account, config)
            config.close()
        try:
            conn = psycopg2.connect(database=db_account['db_name'],
                                    user=db_account['login'],
                                    password=db_account['password'])
        except:
            print('Некоректные данные для подключения к БД')
            os.remove('config.json')
            print()
            continue
        flag = True
    print('Соединение c БД успешно создано')
    time.sleep(3)
    return conn
#_____________________________________________________________________________


def display_menu():
    """
    Функция вывода на экран главного меню программы.

    Функция выводит на экран главное меню программы и запрашивает выбор пункта
    от пользователя. Производится проверка на корректность пользовательского
    ввода. Результатам работы функции является номер выбранного пункта меню
    :return: номер выбранного пункта меню
    """
    choice = -1
    while choice == -1:
        print()
        print('0. Создать/очистить таблицы БД')
        print('1. Сформировать первичное заполнение БД')
        print('=======================================')
        print('2. Добавить данные нового заказчика')
        print('3. Добавить телефон заказика')
        print('4. Изменить данные заказчика')
        print('5. Удалить телефон заказчика')
        print('6. Удалить все данные заказчика')
        print('7. Найти заказчика по атрибутам')
        print('========================================')
        print('8. Завершить работу')
        print()
        flag = False
        while flag == False:
            try:
                choice = int(input('Введите номер пункта меню: '))
                print()
            except ValueError:
                print('Необходимо ввести число от 0 до 8')
                print()
                continue
            if choice < 0 or choice > 8:
                print('Необходимо ввести число от 0 до 8')
                print()
                continue
            flag = True
    return choice
#_____________________________________________________________________________


def display_client_edit_menu():
    """
    Функция вывода на экран меню редактирования данных о заказчике.

    Функция выводит на экран дополнительное меню редактирования данных
    о заказчике. Производится проверка на корректность пользовательского
    ввода. Результатам работы функции является номер выбранного пункта меню
    :return: номер выбранного пункта меню
    """
    choice = 0
    while choice == 0:
        print('1. Скорректировать имя')
        print('2. Скорректировать фамилию')
        print('3. Скорректировать е-мейл')
        print('4. Завершить корректировку')
        print()
        flag = False
        while flag == False:
            try:
                choice = int(input('Введите номер пункта меню: '))
            except ValueError:
                print('Необходимо ввести число от 0 до 7')
                print()
                continue
            if choice < 0 or choice > 7:
                print('Необходимо ввести число от 0 до 7')
                print()
                continue
            flag = True
    return choice
#_____________________________________________________________________________


def check_client_email(conn, control_type, pre_explanation, post_explanation):
    """
    Функция ввод и проверки е-мейл.

    Функция запрашивает ввод е-мейл, после чего проверяется соответствие емейл
    требованиям ("@" и ".") и выполняется проверка е-мейл на существование в
    базе согласно параметру control_type
    :param conn: соединение с БД
    :param control_type:
        1 - Требуется наличие заказчика в базе. Поэтому, в случае отсуствия
                в базе емейл, ввод повторяется до тех пор, пока не будет
                введен емейл, присутствующий в базе
        2 - Требуется отсуствие заказчика в базе. Поэтому ввод повторяется до
                тех пор, пока не будет введен емейл, отсутствующий в базе

    :param pre_explanation, post_explanation:
            контекстные пояснения для пользователя, которые импортируются
            в приглашение ввести е-мейл клиента
    :return: введенный пользователем е-мейл, проверенный согласно control_type
    """
    with conn.cursor() as cur:
        while True:
            client_email = input(f'Введите {pre_explanation}е-мейл '
                                 f'{post_explanation}заказчика: ')
            if '@' and '.' not in client_email:
                print('Данный е-мейл не содержит обязательных символов "@" '
                      'и/или "."')
                pre_explanation = 'повторно ' + pre_explanation
                continue

            cur.execute("""
            SELECT * FROM clients
            WHERE email=%s;                   
               """, (client_email,))
            conn.commit()
            client = cur.fetchone()
            if client != None:
                print(f'Заказчик {client[1]} {client[2]} c данным email '
                      f'присутствует в базе')
                if control_type == 1:
                    print()
                    return client_email
                else:
                    print('Новый или измененный емейл д.б. уникален. '
                          'Попробуйте вести емейл еще раз')
                    print()
                    continue
            else:
                print(f'Данный емейл {client_email} не присутствует в базе, '
                      f'', end='')
                if control_type == 2:
                    print('и может быть безопасно добавлен')
                    return client_email
                else:
                    print('в связи с чем запись клиента не может быть найдена.'
                          ' Попробуйте вести емейл еще раз')
                    print()
#_____________________________________________________________________________


def check_client_phone():
    """
    Функция ввода и проверки телефонного номера.

    Функция позволяет ввести 11-ти значный телефонный номер, проверяет его
    на размер и отсутствие не-цифр и добавляет символы +, (, ), -
    :return: телефонный номер в формате строки
    """
    iteration = ''
    while True:
        client_phone_str = input(f'Введите {iteration}11 цифр телефона '
                                 f'заказчика: +')
        try:
            int(client_phone_str)
        except ValueError:
            print('Необходимо ввести только цифры')
            iteration = 'повторно '
            continue

        if len(client_phone_str) != 11:
            print('Необходимо ввести строго 11 цифр')
            iteration = 'повторно '
            continue
        break

    client_phone_str = ('+' + client_phone_str[0] + '(' +
                        client_phone_str[1:4] + ')' +
                        client_phone_str[4:7] + '-' +
                        client_phone_str[7:]
                        )

    return client_phone_str
#_____________________________________________________________________________


def check_numeric_input(allowed_points, explanation):
    """
    Функция проверки ввода натурального числа.

    На вход функции подается список значений - натуральных чисел, -
    допустимых для ввода, далее функция обеспечивает ввод и проверку ввода
    на вхождение в данный список значений.
    :param allowed_points: списко допустимых значений
    :param explanation: пояснение для приглашения пользователю
    :return: число - значение выбора пользователя
    """
    flag = False
    while flag == False:
        try:
            choice = int(input(f'Введите {explanation}: '))
            print()
        except ValueError:
            print(f'Необходимо ввести число')
            print()
            continue
        if choice not in allowed_points:
            print(f'Необходимо ввести число из диапазона {allowed_points}')
            print()
            continue
        flag = True

    return choice
#_____________________________________________________________________________
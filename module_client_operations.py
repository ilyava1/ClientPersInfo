import time
import  module_service

def add_new_client(conn):
    """
    Функция добавления нового заказчика в БД

    :param conn: открытое соединение с БД
    :return: None
    """
    with conn.cursor() as cur:
        while True:
            client_name = input('Введите имя заказчика: ')
            client_soname = input('Введите фамилию заказчика: ')
            cur.execute("""
            SELECT * FROM clients
            WHERE name=%s and soname=%s;                   
            """, (client_name, client_soname))
            conn.commit()
            client = cur.fetchall()
            if client != []:
                print(f'Заказчик(и) c такими именем и фамилией уже '
                      f'присутствует(ют) в базе:')
                for i in range(len(client)):
                    print(f'    id: {client[i][0]}')
                    print(f'    Имя: {client[i][1]}')
                    print(f'    Фамилия: {client[i][2]}')
                    print(f'    Email: {client[i][3]}')
                    print()
                while True:
                    try:
                        choice = int(input('Введите 1 - скорректировать '
                                           'имя/фамилию или 2 - перейти '
                                           'к вводу емейл: '))
                    except ValueError:
                        print('Введите цифру')
                        continue
                    if choice < 1 or choice > 2:
                        print('Введите цифру 1 или 2')
                        continue
                    break
                if choice ==1:
                    continue
                else:
                    break

            client_email = module_service.check_client_email(conn, 2, '',
                                                             'данного ')

            cur.execute("""
            INSERT INTO clients (name, soname, email)
            VALUES (%s, %s, %s) RETURNING name, soname;                   
            """, (client_name, client_soname, client_email))
            conn.commit()

            added_client = cur.fetchone()
            if added_client == None:
                print('E-mail должен быть уникальным в базе')
                continue
            else:
                print(f'Заказчик {added_client[0]} {added_client[1]} c email '
                      f'{client_email} добавлен в базу')
                print()
                break

    return
#_____________________________________________________________________________


def add_new_phone(conn):
    """
    Функция добавления нового телефона заказчика

    :param conn: открытое соединение с БД
    :return: None
    """
    client_email = module_service.check_client_email(conn, 1, '',
                                                     'существующего ')

    client_phone = module_service.check_client_phone()

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO phones (client_id, phone_number)
            VALUES (
                (SELECT id FROM clients WHERE email=%s),
                (%s))
            RETURNING phone_number;                   
        """, (client_email, client_phone))
        conn.commit()
        print(f'Телефон {cur.fetchone()} добавлен в базу')

    return
#_____________________________________________________________________________


def edit_client_info(conn):
    """
    Функция редактирования информации о заказчике

    :param conn: открытое соединение с БД
    :return: None
    """
    with conn.cursor() as cur:
        client_email = module_service.check_client_email(conn, 1, '',
                                                         'существующего ')
        choice = 0
        while choice != 4:
            choice = module_service.display_client_edit_menu()
            if choice == 1:
                client_name = input('Введите новое имя заказчика: ')
                cur.execute("""
                            UPDATE clients SET name=%s
                            WHERE email=%s
                            RETURNING name;                   
                        """, (client_name,client_email))
                conn.commit()
                print(f'Новое имя заказчика - {cur.fetchone()[0]} - сохранено '
                      f'в базе')
                print()
                time.sleep(2)
                continue

            if choice == 2:
                client_soname = input('Введите новую фамилию заказчика: ')
                cur.execute("""
                            UPDATE clients SET soname=%s
                            WHERE email=%s
                            RETURNING soname;                   
                        """, (client_soname, client_email))
                conn.commit()
                print(f'Новая фамилия заказчика - {cur.fetchone()[0]} - '
                      f'сохранена в базе')
                print()
                time.sleep(2)
                continue

            if choice == 3:
                new_client_email = module_service.check_client_email(conn, 2,
                                            'скорректированный ', 'данного ')

                cur.execute("""
                            UPDATE clients
                            SET email=%s
                            WHERE email=%s;                   
                            """, (new_client_email, client_email))
                conn.commit()
                print(f'Новый е-мейл - {new_client_email} - данного заказчика '
                      f'сохранен в базе')
                print()
                time.sleep(2)
                continue

            if choice == 4:
                return
#_____________________________________________________________________________


def del_client_phone(conn):
    """
    Функция удаления телефона заказчика

    :param conn: открыторе соединение с БД
    :return: None
    """
    client_email = module_service.check_client_email(conn, 1, '',
                                                     'существующего ')
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, phone_number FROM phones
            WHERE client_id IN (
                    SELECT id FROM clients
                    WHERE email=%s
                    );                   
            """, (client_email,))
        phones = cur.fetchall()
        if phones == []:
            print('По данному клиенту в базе телефонов не зарегистрировано')
            print()
            time.sleep(2)
            return
        else:
            if len(phones) > 1:
                allowed_points = []
                print('По данному заказчику найдены следующие телефоны:')
                for element in phones:
                    print(f'id - {element[0]}, тел. {element[1]}')
                    allowed_points.append(element[0])
                choice_id = module_service.check_numeric_input(allowed_points,
                                                     'id удаляемого телефона')
            else:
                print('По данному клиенту найден следующий телефон:')
                print(f'id - {phones[0][0]}, тел. - {phones[0][1]}')
                choice_activity = module_service.check_numeric_input([1,2],
                                                  '1 - удалить, 2 - отмена')
                if choice_activity == 2:
                    print('Удаление отменено')
                    print()
                    time.sleep(2)
                    return
                else:
                    choice_id = phones[0][0]

            with conn.cursor() as cur:
                cur.execute("""
                        DELETE FROM phones
                        WHERE id=%s
                        RETURNING phone_number;                   
                    """, (choice_id,))
                conn.commit()
                print(f'Телефон {cur.fetchone()[0]} удален из базы')
                print()
                time.sleep(2)
                return
#_____________________________________________________________________________


def del_client_info(conn):
    """
    Функция удаления информации о заказчике из базы.

    Информация удаляется из таблицы клиентов и, каскадно, из таблицы телефонов

    :param conn: открытое соединение
    :return: None
    """
    client_email = module_service.check_client_email(conn, 1, '',
                                                     'удаляемого ')
    choice_activity = module_service.check_numeric_input([1, 2], '1 - удалить'
                             ' все данные о заказчике, 2 - отменить удаление')
    if choice_activity == 2:
        print('Удаление отменено')
        print()
        time.sleep(2)
        return
    else:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM clients
                WHERE email=%s
                RETURNING name, soname;                   
                """, (client_email,))
            conn.commit()
            deleted_client = cur.fetchone()
            print(f'Данные заказчика {deleted_client[0]} {deleted_client[1]} '
                  f'удалены из базы')
            print()
            time.sleep(2)
            return
#_____________________________________________________________________________


def find_client(conn):
    """
    Функция поиска клиента по атрибутам

    :param conn: открытое соединение с БД
    :return: None
    """
    name_str = '%' + input('Введите имя заказчика или его фрагмент (или Enter'
                           ' -  пропустить шаг): ') + '%'
    soname_str = '%' + input('Введите фамилию заказчика или его фрагмент (или '
                             'Enter -  пропустить шаг): ') + '%'
    email_str = '%' + input('Введите email заказчика или его фрагмент (или '
                            'Enter -  пропустить шаг): ') + '%'
    phone_str = '%' + input('Введите телефон заказчика или его фрагмент, '
                         'только цифры (или Enter -  пропустить шаг): ') + '%'

    if phone_str != '%%':
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM clients c
                INNER JOIN phones p ON c.id = p.client_id  
                WHERE name LIKE %s AND soname LIKE %s AND email LIKE %s
                AND c.id IN (
                    SELECT client_id FROM phones 
                    WHERE phone_number LIKE %s
                )
                GROUP BY c.id, p.id   
                ORDER BY c.id                
            """, (name_str, soname_str, email_str, phone_str))
            conn.commit()
            found_clients = cur.fetchall()
            print()
            if found_clients == None:
                print('Записей не найдено')
                print('Если у клиента нет телефона - он не будет найден данным'
                      ' запросом. Попробуйте поиск без телефона')
                print()
                time.sleep(3)
                return
            else:
                print('Результат поиска:')
                for client in found_clients:
                    print(f'id - {client[0]}, {client[1]} {client[2]}, '
                          f'{client[3]}, {client[6]}')
                print()
                time.sleep(3)
                return
    else:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM clients c 
                LEFT JOIN phones p ON c.id = p.client_id 
                WHERE name LIKE %s AND soname LIKE %s AND email LIKE %s 
                GROUP BY c.id, p.id   
                ORDER BY c.id            
            """, (name_str, soname_str, email_str))
            conn.commit()
            found_clients = cur.fetchall()
            print()
            if found_clients == None or found_clients == []:
                print('Записей не найдено')
                print()
                time.sleep(3)
                return
            print('Результат поиска:')
            for client in found_clients:
                print(f'id - {client[0]}, {client[1]} {client[2]}, '
                      f'{client[3]}, {client[6]}')
            print()
            time.sleep(3)
            return
#_____________________________________________________________________________
import time
import pandas as pd

def create_db(conn):
    """
    Функция создания таблиц БД.

    Функция получает на вход открытое соединение с БД, после чего удаляет две
    таблицы - телефонов и клиентов, - а после этого создает их заново. Таблицы
    создаются пустыми.
    :param conn: открытое в вызывающем блоке соединение
    :return: None
    """
    with conn.cursor() as cur:
        cur.execute("""
            DROP TABLE if EXISTS phones;
            DROP TABLE if EXISTS clients        
        """)
        conn.commit()

        cur.execute("""
            CREATE TABLE if not EXISTS clients (
                id SERIAL PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                soname VARCHAR(40) NOT NULL,
                email VARCHAR(40) NOT NULL UNIQUE
            );
            CREATE TABLE if not EXISTS phones (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL REFERENCES clients
                ON DELETE CASCADE,                
                phone_number VARCHAR(15) UNIQUE
            );
            """)
        conn.commit()

        print("Таблицы БД подготовлены для наполнения")

    return
#_____________________________________________________________________________


def load_data(conn):
    """
    Функция первоначального заполнения БД.

    Функция получает на вход открытое соединение с БД, после чего производит
    наполнение базовым содержимым таблицы клиентов и телефонов. По результату
    на экран выводится сводная таблица с данными из базы.
    :param conn: открытое в вызывающем блоке соединение
    :return: None
    """
    create_db(conn)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (name, soname, email)
            VALUES
                ('Harry', 'Potter', 'hpotter@hogwards.mk'),
                ('Germiona', 'Granger', 'ggranger@hogwards.mk'),
                ('Ron', 'Weesley', 'rweesley@hogwards.mk'),
                ('Nevill', 'Dolgopups', 'ndolgopups@hogwards.mr'),
                ('Albus', 'Dumbldore', 'adumbldore@hogwards.mr'),
                ('Severus', 'Snape', 's_snape@hogwards.mr')
            RETURNING name, soname;  
        """)
        conn.commit()

        cur.execute("""
                    INSERT INTO phones (client_id, phone_number)
                    VALUES
                        (1, '+1(000)111-7770'),
                        (1, '+1(000)111-7771'), 
                        (2, '+1(000)111-5550'), 
                        (2, '+1(000)111-5551'), 
                        (3, '+1(000)111-4440'),  
                        (3, '+1(000)111-4441'),  
                        (4, '+1(000)111-3330'),  
                        (6, '+1(000)111-1110')
                    RETURNING phone_number;
                """)
        conn.commit()

        cur.execute("""
                       SELECT * FROM clients c 
                       FULL OUTER JOIN phones p ON c.id = p.client_id                       
                       GROUP BY c.id, p.id   
                       ORDER BY c.id;            
                   """)
        conn.commit()
        result = cur.fetchall()
        if result == None:
            print('Ошибка при добавлении записей')
            print()
            time.sleep(2)
            return
        else:
            print('Результат первичного наполнения:')
            print()
            df = pd.DataFrame(result, columns=['id заказчика', 'имя', 'фамилия', 'почта', 'id тел', 'id заказчика', 'телефон'])
            print(df.to_string(index=False))
            print()
            time.sleep(3)
            return
#_____________________________________________________________________________
# Домашнее задание «Работа с PostgreSQL из Python»

import module_service
import module_db_core
import module_client_operations

if __name__ == '__main__':

    conn = module_service.ask_for_db_access()

    while True:
        choice = module_service.display_menu()
        if choice == 0:
            module_db_core.create_db(conn)
        elif choice == 1:
            module_db_core.load_data(conn)
        elif choice == 2:
            module_client_operations.add_new_client(conn)
        elif choice == 3:
            module_client_operations.add_new_phone(conn)
        elif choice == 4:
            module_client_operations.edit_client_info(conn)
            continue
        elif choice == 5:
            module_client_operations.del_client_phone(conn)
        elif choice == 6:
            module_client_operations.del_client_info(conn)
        elif choice == 7:
            module_client_operations.find_client(conn)
        else:
            print()
            conn.close()
            print('Работа программы завершена')
            exit()

        input('Для продолжения нажмите Enter ')

import psycopg2
from pprint import pprint


def create_db(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS info_clients(
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(40),
        last_name VARCHAR(40),
        email VARCHAR(40)
        );
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS phone_numbers(
        id SERIAL PRIMARY KEY,
        info_clients_id INTEGER REFERENCES info_clients(id),
        phone VARCHAR(200)
        );
    """)
    return


def delete_db(conn):
    conn.execute("""
        DROP TABLE info_clients, phone_numbers CASCADE;
        """)

def add_phone(conn, info_clients_id, phone):
    conn.execute("""
        INSERT INTO phone_numbers(phone, info_clients_id)
        VALUES (%s, %s)
        """, (phone, info_clients_id))
    return info_clients_id

def add_client(conn, first_name=None, last_name=None, email=None, phone=None):
    conn.execute("""
        INSERT INTO info_clients(first_name, last_name, email)
        VALUES (%s, %s, %s)
        """, (first_name, last_name, email))
    conn.execute("""
        SELECT id from info_clients
        ORDER BY id DESC
        LIMIT 1
        """)
    id = conn.fetchone()[0]
    if phone is None:
        return id
    else:
        add_phone(conn, id, phone)
        return id


def change_client(conn, id, first_name=None, last_name=None, email=None):
    conn.execute("""
        SELECT * from info_clients
        WHERE id = %s
        """, (id, ))
    info = conn.fetchone()
    if first_name is None:
        first_name = info[1]
    if last_name is None:
        last_name = info[2]
    if email is None:
        email = info[3]
    conn.execute("""
        UPDATE info_clients
        SET first_name = %s, last_name = %s, email =%s
        where id = %s
        """, (first_name, last_name, email, id))
    return id


def delete_phone(conn, phone):
    conn.execute("""
        DELETE FROM phone_numbers
        WHERE phone = %s
        """, (phone,))
    return phone


def delete_client(conn, id):
    conn.execute("""
        DELETE FROM phone_numbers
        WHERE info_clients_id = %s
        """, (id, ))
    conn.execute("""
        DELETE FROM info_clients
        WHERE id = %s
       """, (id,))
    return id


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    if first_name is None:
        first_name = '%'
    else:
        first_name = '%' + first_name + '%'
    if last_name is None:
        last_name = '%'
    else:
        last_name = '%' + last_name + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if phone is None:
        conn.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM info_clients c
            LEFT JOIN phone_numbers p ON c.id = p.info_clients_id
            WHERE c.first_name LIKE %s AND c.last_name LIKE %s
            AND c.email LIKE %s
            """, (first_name, last_name, email))
    else:
        conn.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM info_clients c
            LEFT JOIN phone_numbers p ON c.id = p.info_clients_id
            WHERE c.first_name LIKE %s AND c.last_name LIKE %s
            AND c.email LIKE %s AND p.number like %s
            """, (first_name, last_name, email, phone))
    return conn.fetchall()


with psycopg2.connect(database="clients_db", user="postgres", password="33851") as conn:
    with conn.cursor() as DB:
    # 1. Удаление базы данных
        delete_db(DB)
        print("База данных удалена")

    # 2. Создание базы данных
        create_db(DB)
        print("База данных создана")

    # 3. Добавление клиентов
        print("Добавлен клиент id: ",
            add_client(DB, "Иван", "Иванов", "qwert@mail.ru"))
        print("Добавлен клиент id: ",
            add_client(DB, "Василий", "Васин",
                                "asdfg@mail.ru", 79991112233))

    # 4. Добаляем номера телефона
        print("Телефон добавлен клиенту id: ",
            add_phone(DB, 1, 79991112222))
        print("Телефон добавлен клиенту id: ",
            add_phone(DB, 2, 79991112211))

    # 4. Изменим данные клиентjd
        print("Изменены данные клиента id: ",
            change_client(DB, 1, "Сергей", "Сергеев", None))

    # # 5. Удаляем номер телефона клиента
        print("Номер телефона удален: ",
            delete_phone(DB, '79991112211'))

    # 6. Удалим клиента номер 1
        print("Клиент удалён с id: ",
            delete_client(DB, 2))

    # 7. Найдём клиента
        print('Найденный клиент по имени:')
        pprint(find_client(DB, None, 'Сергеев'))

DB.close()

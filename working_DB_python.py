import psycopg2


def creating_database_structure(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS Client(
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        email VARCHAR(40) UNIQUE NOT NULL
                    );
                    """)

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS Phone(
                        id SERIAL PRIMARY KEY,
                        number_phone VARCHAR(20) UNIQUE
                    );
                    """)

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS ClientPhone(
                        client_id INTEGER references Client(id),
                        phone_id INTEGER references Phone(id),
                        constraint pk PRIMARY KEY (client_id, phone_id)
                        );
                    """)
        conn.commit()

def add_new_client(conn, first_name, last_name, email, number_phone = None):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO Client(first_name, last_name, email) VALUES(%s, %s, %s) RETURNING id;
                    """, (first_name, last_name, email))
        id_client = cur.fetchone()[0]

        if number_phone:
            cur.execute("""
                        INSERT INTO Phone(number_phone) VALUES(%s) RETURNING id;""", (number_phone,))
            id_phone = cur.fetchone()[0]

            cur.execute("""
                        INSERT INTO ClientPhone(client_id, phone_id) VALUES(%s, %s);""", (id_client, id_phone))
            conn.commit()

def add_phone_client(conn, client_id, number_phone):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO Phone(number_phone) VALUES(%s) RETURNING id;""", (number_phone,))
        id_phone = cur.fetchone()[0]

        cur.execute("""
                    INSERT INTO ClientPhone(client_id, phone_id) VALUES(%s, %s);""", (client_id, id_phone))
        conn.commit()

def update_info_client(conn, client_id, first_name = None, last_name = None, email = None, number_phone = None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
                        UPDATE Client SET first_name = %s WHERE id = %s;
                        """, (first_name, client_id))
            conn.commit()
        if last_name:
            cur.execute("""
                        UPDATE Client SET last_name = %s WHERE id = %s;
                        """, (last_name, client_id))
            conn.commit()
        if email:
            cur.execute("""
                        UPDATE Client SET email = %s WHERE id = %s;
                        """, (email, client_id))
            conn.commit()

        if number_phone:
            cur.execute("""
                        SELECT p.id, p.number_phone FROM Phone p
                          JOIN ClientPhone cp ON p.id = cp.phone_id
                         WHERE cp.client_id = %s;
                        """, (client_id,))
            print(f'У выбранного клиента следующие телефоны\n {cur.fetchall()}')
            id_phone = input('Выберите телефон, который хотите изменить: ')

            cur.execute("""
                        UPDATE Phone SET number_phone = %s WHERE id = %s;
                        """, (number_phone, id_phone))
            conn.commit()

def delete_telefon_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT p.id, p.number_phone FROM Phone p
                      JOIN ClientPhone cp ON p.id = cp.phone_id
                     WHERE cp.client_id = %s;
                    """, (client_id,))
        print(f'У выбранного клиента следующие телефоны\n {cur.fetchall()}')
        id_phone = input('Выберите телефон, который хотите удалить: ')

        cur.execute("""
                    DELETE FROM ClientPhone WHERE phone_id = %s;
                    """, (id_phone,))
        conn.commit()

        cur.execute("""
                    DELETE FROM Phone WHERE id = %s;
                    """, (id_phone,))

def delete_client(conn, client_id):
    phone_id_list = []
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT p.id, p.number_phone FROM Phone p
                      JOIN ClientPhone cp ON p.id = cp.phone_id
                     WHERE cp.client_id = %s;
                    """, (client_id,))
        phone_id_list.extend(cur.fetchall())

        cur.execute("""
                    DELETE FROM ClientPhone WHERE client_id = %s;
                    """, (client_id,))
        conn.commit()

        cur.execute("""
                    DELETE FROM Client WHERE id = %s;
                    """, (client_id,))
        conn.commit()

        for id_phone, phone_number in phone_id_list:
            cur.execute("""
                        DELETE FROM Phone WHERE id = %s;
                        """, (id_phone,))
            conn.commit()

def find_client(conn, first_name = None, last_name = None, email = None, number_phone = None):
    with conn.cursor() as cur:
        if first_name is None and last_name is None and email is None and number_phone is None:
            print('Для поиска клиента не задано ни одного параметра. Выведен полный список клиентов.')
            cur.execute("""
                       SELECT c.id, c.first_name, c.last_name, c.email, p.number_phone FROM Client c
                         JOIN ClientPhone cp ON c.id = cp.client_id
                         JOIN Phone p ON cp.phone_id = p.id
                       """)
            print(cur.fetchall())
        elif first_name is not None and last_name is not None and email is not None and number_phone is not None:
            cur.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.number_phone FROM Client c
                          JOIN ClientPhone cp ON c.id = cp.client_id
                          JOIN Phone p ON cp.phone_id = p.id
                         WHERE c.first_name ILIKE %s 
                           AND c.last_name ILIKE %s 
                           AND c.email ILIKE %s 
                           AND p.number_phone ILIKE %s;
                        """, (first_name, last_name, email, number_phone))
            print(cur.fetchall())
        elif first_name is not None and last_name is not None and email is not None:
            cur.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.number_phone FROM Client c
                          JOIN ClientPhone cp ON c.id = cp.client_id
                          JOIN Phone p ON cp.phone_id = p.id
                         WHERE c.first_name ILIKE %s 
                           AND c.last_name ILIKE %s 
                           AND c.email ILIKE %s 
                        """, (first_name, last_name, email))
            print(cur.fetchall())
        elif first_name is not None and last_name is not None:
            cur.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.number_phone FROM Client c
                          JOIN ClientPhone cp ON c.id = cp.client_id
                          JOIN Phone p ON cp.phone_id = p.id
                         WHERE c.first_name ILIKE %s 
                           AND c.last_name ILIKE %s 
                        """, (first_name, last_name))
            print(cur.fetchall())
        elif first_name is not None:
            cur.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.number_phone FROM Client c
                          JOIN ClientPhone cp ON c.id = cp.client_id
                          JOIN Phone p ON cp.phone_id = p.id
                         WHERE c.first_name ILIKE %s;
                        """, (first_name, ))
            print(cur.fetchall())
        elif last_name is not None:
            cur.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.number_phone FROM Client c
                          JOIN ClientPhone cp ON c.id = cp.client_id
                          JOIN Phone p ON cp.phone_id = p.id
                         WHERE c.last_name ILIKE %s;
                        """, (last_name, ))
            print(cur.fetchall())
        elif email is not None:
            cur.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.number_phone FROM Client c
                          JOIN ClientPhone cp ON c.id = cp.client_id
                          JOIN Phone p ON cp.phone_id = p.id
                         WHERE c.email ILIKE %s;
                        """, (email, ))
            print(cur.fetchall())
        elif number_phone is None:
            cur.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.number_phone FROM Client c
                          JOIN ClientPhone cp ON c.id = cp.client_id
                          JOIN Phone p ON cp.phone_id = p.id
                         WHERE p.number_phone ILIKE %s;
                        """, (number_phone, ))
            print(cur.fetchall())


if __name__ == '__main__':
    with psycopg2.connect(
            host='localhost',
            database='client_db',
            user='postgres',
            password='p1234567/'
    ) as conn:
        # creating_database_structure(conn)
        # add_new_client(conn, first_name='Ivan', last_name='Ivanov', email='123@gmail.com', number_phone='+7(111)222-33-44')
        # add_new_client(conn, first_name='Ivan', last_name='Sidorov', email='777@gmail.com', number_phone='+7(531)654-45-44')
        # add_new_client(conn, first_name='Peter', last_name='Petrov', email='456@gmail.com')
        # add_phone_client(conn, 3, number_phone='+7-555-666-77-88')
        # add_phone_client(conn, 1, number_phone='+7(999)-111-22-33')
        # update_info_client(conn, '2', first_name='Semen', last_name='Sidorov', email='999@gmail.com', number_phone='+7(777)777-77-77')
        # delete_telefon_client(conn, '1')
        # delete_client(conn, '3')
        find_client(conn)
        find_client(conn, email='999@gmail.com')
    conn.close()
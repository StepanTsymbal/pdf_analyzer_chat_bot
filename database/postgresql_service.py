import psycopg2
from datetime import datetime


# TODO: move to variables
DB_USER = "postgres"
DB_PASSWORD = "pass1234"
DB_NAME = "chat_bot"
DB_HOST = "localhost"

connection = psycopg2.connect(user=DB_USER,
                                  password=DB_PASSWORD,
                                  host=DB_HOST,
                                  # port="5432",
                                  database=DB_NAME)

cursor = connection.cursor()


def create_documents_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS documents
    (id SERIAL PRIMARY KEY NOT NULL,
    uuid TEXT NOT NULL,
    name TEXT NOT NULL)
    '''

    cursor.execute(create_table_query)
    connection.commit()


def create_chat_history_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS chat_history
    (id SERIAL PRIMARY KEY NOT NULL,
    text TEXT NOT NULL,
    is_question BOOL,
    document_id INT NOT NULL,
    session_id TEXT NOT NULL,
    created_time TIMESTAMP NOT NULL,
    CONSTRAINT fk_document FOREIGN KEY(document_id) REFERENCES documents(id))
    '''

    cursor.execute(create_table_query)
    connection.commit()


def insert_documents_row(uuid, name):
    insert_query = """
        INSERT INTO documents (uuid, name) 
        VALUES ('{uuid}', '{name}')
        returning id
        """.format(uuid=uuid, name=name)

    cursor.execute(insert_query)
    document_id = cursor.fetchone()[0]
    connection.commit()

    return document_id


def insert_chat_history_row(text, is_question, document_id, session_id):
    insert_query = """
        INSERT INTO chat_history (text, is_question, document_id, session_id, created_time) 
        VALUES ('{text}', {is_question}, {document_id}, '{session_id}', '{created_time}')
        """.format(text=text, is_question=is_question, document_id=document_id, session_id=session_id, created_time=datetime.now())

    cursor.execute(insert_query)
    connection.commit()


def get_all_documents():
    get_query = 'SELECT * FROM documents'

    cursor.execute(get_query)
    connection.commit()

    return cursor.fetchall()


def get_document_by_id(id):
    get_query = '''
    SELECT * FROM documents
    WHERE id = '{id}'
    '''.format(id=id)

    cursor.execute(get_query)
    connection.commit()

    return cursor.fetchone()


# create_documents_table()
# insert_row('asdasd', 'name_test_3')
# print(get_all_documents())

# create_chat_history_table()
# insert_chat_history_row('text_text_1', True, 30, 'asd-asdasd-asd')

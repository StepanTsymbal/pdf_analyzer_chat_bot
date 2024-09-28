import psycopg2
from datetime import datetime
import logging


# TODO: move to variables
DB_USER = "postgres"
DB_PASSWORD = "pass1234"
DB_NAME = "chat_bot"
DB_HOST = "localhost"


def get_db_connection():
    connection = psycopg2.connect(user=DB_USER,
                                  password=DB_PASSWORD,
                                  host=DB_HOST,
                                  # port="5432",
                                  database=DB_NAME)

    logging.info('postgres_service:: connection initialized')

    return connection


def create_documents_table():
    connection = get_db_connection()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS documents
    (id SERIAL PRIMARY KEY NOT NULL,
    uuid TEXT NOT NULL,
    name TEXT NOT NULL)
    '''

    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()

    logging.info('postgres_service:: documents table initialized')


def create_chat_history_table():
    connection = get_db_connection()

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

    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()

    logging.info('postgres_service:: chat history table initialized')


def insert_documents_row(uuid, name):
    connection = get_db_connection()

    insert_query = """
        INSERT INTO documents (uuid, name) 
        VALUES (%s, %s)
        returning id
        """

    data = (str(uuid), name)

    with connection.cursor() as cursor:
        cursor.execute(insert_query, data)
        document_id = cursor.fetchone()[0]
        connection.commit()

    logging.info('postgres_service:: documents row inserted')

    return document_id


def insert_chat_history_row(text, is_question, document_id, session_id):
    connection = get_db_connection()

    insert_query = """
        INSERT INTO chat_history (text, is_question, document_id, session_id, created_time) 
        VALUES (%s, %s, %s, %s, %s)
        """

    data = (text, is_question, document_id, str(session_id), str(datetime.now()))

    with connection.cursor() as cursor:
        cursor.execute(insert_query, data)
        connection.commit()

    logging.info('postgres_service:: chat history row inserted')


def get_all_documents():
    connection = get_db_connection()

    get_query = 'SELECT * FROM documents'

    with connection.cursor() as cursor:
        cursor.execute(get_query)
        connection.commit()

        documents = cursor.fetchall()

    return documents


def get_document_by_id(id):
    connection = get_db_connection()

    get_query = '''
    SELECT * FROM documents
    WHERE id = '{id}'
    '''.format(id=id)

    with connection.cursor() as cursor:
        cursor.execute(get_query)
        connection.commit()
        document = cursor.fetchone()

    return document


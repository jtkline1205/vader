import psycopg2
from app.socketio_instance import socketio

db_params = {
    'dbname': 'neptune-data',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': '5432',
}

def fetch_all(table_name, where_column, value_match):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM {} WHERE {} = {}'.format(table_name, where_column, value_match))
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, row)) for row in data]
    return result

def fetch_all_with_two_conditions(table_name, where_column_1, value_match_1, where_column_2, value_match_2):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM {} WHERE {} = {} AND {} = {}'.format(table_name, where_column_1, value_match_1, where_column_2, value_match_2))
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, row)) for row in data]
    return result

def fetch_one(query_string, id):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(query_string, (id, ))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def fetch_one_column(column, table_name, where_column, value_match):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute('SELECT {} FROM {} WHERE {} = {}'.format(column, table_name, where_column, value_match))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def update_one(query_string, new_value, id):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(query_string, (new_value, id,))
    connection.commit()
    cursor.close()
    connection.close()
    socketio.emit('data_changed', namespace='/')


def update_one_column(table_name, column_to_set, new_value, where_column, value_match):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute('UPDATE {} SET {}={} WHERE {} = {}'.format(table_name, column_to_set, new_value, where_column, value_match))
    connection.commit()
    cursor.close()
    connection.close()
    socketio.emit('data_changed', namespace='/')

def update_one_column_with_two_conditions(table_name, column_to_set, new_value, where_column_1, value_match_1, where_column_2, value_match_2):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute('UPDATE {} SET {}={} WHERE {} = {} AND {} = {}'.format(table_name, column_to_set, new_value, where_column_1, value_match_1, where_column_2, value_match_2))
    connection.commit()
    cursor.close()
    connection.close()
    socketio.emit('data_changed', namespace='/')


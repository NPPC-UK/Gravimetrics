import sys
from hashlib import sha512
import pymysql
import pymysql.cursors
from statements import get_staff_sql, get_salt_sql, get_name_passwd_sql
from conn_manager import create_connection


def login_user(app, uname, pwd):

    try:
        conn = create_connection('auth')
        if conn is None:
            raise pymysql.err.DatabaseError

        return is_user(conn,
                       uname,
                       pwd)

    except pymysql.err.DatabaseError as e:
        print(e)
        return False


def get_user_salt(conn, user):
    """
    This will connect to the database and look up the hash and salt
    of a given user and return them if the user exists
    """
    try:
        with conn.cursor() as cursor:
            sql = get_salt_sql.format(user)
            cursor.execute(sql)
            result = cursor.fetchall()
            if result is None:
                raise pymysql.err.DatabaseError
            elif result:
                for entry in result:
                    return entry['salt']
            else:
                raise pymysql.err.DataError

    except (pymysql.err.DatabaseError,
            pymysql.err.IntegrityError,
            pymysql.err.MySQLError,
            pymysql.err.DataError) as exception:
        print(exception)


def get_hash(conn, passwd, salt):
    """
    This takes a password and salt and verifies it against what is in the database for users
    Uses sha512 which is part of the python haslib standard library
    """
    # first running

    hashed = sha512(passwd.encode('utf-8') +
                    salt.encode('utf-8')).hexdigest()

    # then run the next 100 times
    for x in range(0, 100):
        hashed = sha512(hashed.encode('utf-8') +
                        str(x).encode('utf-8')).hexdigest()

    return hashed


def is_user(conn, user, password):
    """
    Checks if the user and password given are valid
    returns a bool to indicate this
    """
    try:
        salt = get_user_salt(conn, user)
        genhash = get_hash(conn, password, salt).encode('utf-8')
        with conn.cursor() as cursor:
            sql = get_name_passwd_sql.format(user, genhash.decode('utf-8'))
            cursor.execute(sql)
            result = cursor.fetchall()
            if result:
                return True
            else:
                return False  # problem with loading

    except (pymysql.err.DatabaseError,
            pymysql.err.IntegrityError,
            pymysql.err.MySQLError,
            AttributeError) as exception:
        print(exception)
        return False

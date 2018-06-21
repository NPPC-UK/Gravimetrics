import pymysql


def get_dbinfo():
    info = {}
    info['host'] = None
    info['user'] = None
    info['passwd'] = None
    info['auth'] = None
    info['gravi'] = None

    with open('dbinfo.dat') as dat:
        info['host'] = dat.readline().rstrip('\n')
        info['user'] = dat.readline().rstrip('\n')
        info['passwd'] = dat.readline().rstrip('\n')
        info['auth'] = dat.readline().rstrip('\n')
        info['gravi'] = dat.readline().rstrip('\n')

    return info


def create_connection(database):
    """
    This creates a connection object
    to the database and returns it for use
    """
    # reset the object in memory
    dbinfo = get_dbinfo()
    conn = None
    try:
        conn = pymysql.connect(dbinfo['host'],
                               dbinfo['user'],
                               dbinfo['passwd'],
                               dbinfo[database],
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

    except (pymysql.err.DatabaseError,
            pymysql.err.IntegrityError,
            pymysql.err.MySQLError) as exception:
        print(exception)
        return None

    return conn

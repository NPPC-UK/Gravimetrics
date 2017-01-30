"""
This file contains some connection object information 
that is needed to connect to the gravimetrics database 

Currently there is a glaring ISSUE that this pulls data using balance_id
really should use plant_id but need a sql wizard to help 
"""

import sys
import pymysql.cursors
import pymysql
from plants import Plant as plant_data


class Connection(object):
    """Database connection that can be treated as an object
    that can be passed around other functions
    """

    def __init__(self):
        self.connection = None

    def create_connection(self, host, user, passwd, database):
        """This creates a connection object\
        to the database and returns it for use
        """
        try:
            self.connection = pymysql.connect(host,
                                              user,
                                              passwd,
                                              database,
                                              charset='utf8mb4',
                                              cursorclass=pymysql.cursors.DictCursor)

        except (pymysql.err.DatabaseError,
                pymysql.err.IntegrityError,
                pymysql.err.MySQLError) as exception:
            sys.stderr.write(str(exception))
            return 2

        finally:
            if self.connection is None:
                sys.stderr.write("Problem connecting to database\n")
        return 0

    def get_watering_history(self, balance_id, num_days=7):
        """
        This will get the most recent readings for a particular balance
        using num_days to denote how far back to check readings 
        """
        try:
            with self.connection.cursor() as cursor:

                sql = "select * from watering_data where balance_id = {0} and logdate >= CURDATE()-{1}".format(
                    balance_id, num_days)

                cursor.execute(sql)
                result = cursor.fetchall()
                plant = plant_data()
                for row in result:
                    if str(row['start_weight']).isdigit() and str(row['end_weight']).isdigit():
                        plant.add_entry(row['start_weight'], row[
                                        'logdate'], end_weight=row['end_weight'])
                    else:
                        continue

        except (pymysql.err.DatabaseError,
                pymysql.err.IntegrityError,
                pymysql.err.MySQLError) as exception:
            sys.stderr.write(exception)
            return 2
        finally:
            pass
        return plant

    def get_balance_history(self, balance_id, num_days):
        """
        This will get the most recent readings for a particular balance
        using num_days to denote how far back to check readings 
        """
        try:
            with self.connection.cursor() as cursor:

                sql = "select logdate, weight from balance_data \
                where balance_id = {0} \
                and logdate > CURDATE()-{1};".format(balance_id, num_days)

                cursor.execute(sql)
                result = cursor.fetchall()
                plant = plant_data()
                for row in result:
                    if str(row['weight']).isdigit():
                        plant.add_entry(row['weight'], row['logdate'])
                    else:
                        continue

        except (pymysql.err.DatabaseError,
                pymysql.err.IntegrityError,
                pymysql.err.MySQLError) as exception:
            sys.stderr.write(exception)
            return 2
        finally:
            pass
        return plant

    def __del__(self):
        """This is the tidy up function for the class
        currently all that it does is to shut the connection
        to the database """
        if self.connection is not None:
            self.connection.close()
            print("Connection closed")
            return 0

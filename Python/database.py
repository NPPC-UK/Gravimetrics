"""
This file contains all of the database interaction for the gravimetrics system
it has facilities to pull data about experiments and plants, and can also
perform some data updates via insert commands.
"""

import sys
import re
import pymysql.cursors
import pymysql
from plants import Plants as plant_data


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
            sys.stderr.write(exception)

        finally:
            if self.connection is None:
                sys.stderr.write("Problem connecting to database\n")
                sys.exit()

    def get_plants(self, pi_num):
        """Returns a list of current plants under control of pi_num"""
        plants_container = []
        try:
            with self.connection.cursor() as cursor:

                sql = 'select plants.plant_id, plants.target_weight,\
                plants_to_balance.balance_id, balances.address, \
                gpio_pin, balances.pi_assigned, experiment_id from plants\
                left join plants_to_balance using(plant_id)\
                left join balances using(balance_id)\
                left join watering_valves using(balance_id)\
                where pi_assigned = {0} and end_date IS NULL or end_date > curdate()'.format(pi_num)

                cursor.execute(sql, pi_num)
                result = cursor.fetchall()

                for row in result:
                    # Assign details of a plant here
                    tmp_plant = plant_data(row["plant_id"], row["balance_id"],
                                           row["address"], row["gpio_pin"],
                                           row["target_weight"], row["experiment_id"])
                    plants_container.append(tmp_plant)

        except (pymysql.err.DatabaseError,
                pymysql.err.IntegrityError,
                pymysql.err.MySQLError) as exception:
            sys.stderr.write(exception)

        finally:
            pass
        return plants_container

    def perform_weight_update(self, plant):
        """Takes a plant and updates their\
        weighing readings to the database"""
        try:
            with self.connection.cursor() as cursor:
                # Update weight readings
                sql = "INSERT INTO test.balance_data(balance_id, logdate, weight, experiment_id) \
                VALUES ({0}, NOW(), {1}, '{2}')".format(plant.get_balance(),
                                                        plant.get_end_weight(),
                                                        plant.get_experiment_id())

                # Execute our statement
                if is_statement_safe(sql):
                    cursor.execute(sql)
                    self.connection.commit()
                else:
                    print("DANGEROUS STATEMENT")
                    sys.exit()

        # There's quite a few things to go wrong here
        # so I think a broad exception catcher is best
        except (pymysql.err.DatabaseError,
                pymysql.err.IntegrityError,
                pymysql.err.MySQLError) as exception:
            sys.stderr.write(exception)

        finally:
            print("Update has went smoothly")

    def perform_watering_update(self, plant):
        """Takes a plant and uploads their watering\
        data to the database"""
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO test.watering_data(balance_id, logdate, start_weight, \
                end_weight, status, experiment_id)\
                VALUES({0}, NOW(), {1}, {2}, {3}, '{4}')".format(plant.get_balance(),
                                                                 plant.get_start_weight(),
                                                                 plant.get_end_weight(),
                                                                 plant.get_status,
                                                                 plant.get_experiment_id)

                # Execute our statement
                if is_statement_safe(sql):
                    cursor.execute(sql)
                    self.connection.commit()
                else:
                    print("DANGEROUS STATEMENT")
                    sys.exit()
        except (pymysql.err.DatabaseError,
                pymysql.err.IntegrityError,
                pymysql.err.MySQLError) as exception:
            sys.stderr.write(exception)

    def __del__(self):
        """This is the tidy up function for the class
        currently all that it does is to shut the connection
        to the database """
        if self.connection is not None:
            self.connection.close()
            print("Connection closed")


def is_statement_safe(sql_statement):
    """This does a brief check for dangerous SQL """
    regex = re.compile("[^A-Za-z0-9 \'\"]")
    if regex.match(sql_statement):
        return False
    else:
        return True

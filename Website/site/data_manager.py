from conn_manager import create_connection
import pymysql
import pandas as pd


def create_new_experiment(dataframe, owner='NPPC'):
    # create connection
    conn = create_connection('gravi')
    with conn.cursor() as cursor:
        # create experiment
        exp_sql = "INSERT INTO experiment(experiment_id, start_date, end_date, owner) VALUES( \"{0}\", \"{1}\", \"{2}\", \"{3}\"  )"

        experiment_name = dataframe.columns[0]
        start_date = dataframe.columns[1]
        end_date = dataframe.columns[2]
        cursor.execute(
            'INSERT INTO dates(start_date, end_date) VALUES (\"{0}\", \"{1}\")'.format(start_date, end_date))
        cursor.execute(exp_sql.format(
            experiment_name, start_date, end_date, owner))

        # add plants
        plants_sql = "INSERT INTO plants(plant_id, experiment_id, target_weight) VALUES(  \"{0}\", \"{1}\", \"{2}\" )"
        plants_to_balance_sql = 'INSERT INTO plants_to_balance(start_date, end_date, plant_id, balance_id) VALUES(  \"{0}\", \"{1}\", \"{2}\", \"{3}\" )'

        for index, row in dataframe.iterrows():
            cursor.execute(plants_sql.format(row[0],
                                             experiment_name,
                                             row[1]))

            cursor.execute(plants_to_balance_sql.format(start_date,
                                                        end_date,
                                                        row[0],
                                                        row[2]))
        conn.commit()
        return 0


def update_target_weights(dataframe):
    # create connection
    conn = create_connection('gravi')
    with conn.cursor() as cursor:
        try:
            update_statement = "update plants set plants.target_weight = {0} where plants.plant_id='{1}' "
            for index, row in dataframe.iterrows():
                cursor.execute(update_statement.format(row[1], row[0]))
                conn.commit()
        except Exception as e:
            return e
    return 'Successfully updated'


def end_experiment(experiment_id):
    try:
        # create connection
        conn = create_connection('gravi')
        with conn.cursor() as cursor:

            end_sql = "update experiment set experiment.end_date = NOW() where \
                experiment.experiment_id = '{0}'".format(experiment_id)
            cursor.execute(end_sql)
            update_plants_to_balance_sql = "update plants_to_balance left join plants using(plant_id) \
                set plants_to_balance.end_date = NOW() \
                where plants.experiment_id = '{0}' ".format(experiment_id)
            cursor.execute(update_plants_to_balance_sql)
            conn.commit()

            return get_all_water_data(experiment_id)
    except:
        return 2


def get_experiment_plants(experiment_id):
        # create connection
    conn = create_connection('gravi')
    with conn.cursor() as cursor:
        get_plants_sql = "select * from plants where experiment_id = \"{0}\""
        plants = pd.read_sql(get_plants_sql.format(experiment_id),
                             conn)
        return plants


def get_all_balance_data(experiment_id):
    # create connection
    conn = create_connection('gravi')
    with conn.cursor() as cursor:
        get_balance = """
        SELECT bd.balance_id, plants_and_balances.plant_id AS Plant, bd.logdate AS Logdate, bd.weight AS Weight
        FROM
        (
        SELECT p.plant_id, ptb.balance_id
        FROM plants p
        JOIN plants_to_balance AS ptb ON (p.plant_id = ptb.plant_id)
        WHERE p.experiment_id = '{0}'
        ) AS plants_and_balances
        JOIN balance_data bd ON (bd.balance_id = plants_and_balances.balance_id)
        WHERE bd.experiment_id = '{0}'
        ORDER BY plants_and_balances.plant_id, bd.logdate;"""

        print(get_balance.format(experiment_id))
        balance_data = pd.read_sql(get_balance.format(experiment_id),
                                   conn)
        return balance_data


def get_all_water_data(experiment_id):

        # create connection
    conn = create_connection('gravi')
    with conn.cursor() as cursor:
        get_water = """
        SELECT plants_to_balance.balance_id, plants.plant_id, logdate, start_weight, end_weight,  plants.target_weight
        FROM watering_data
        JOIN plants_to_balance ON plants_to_balance.balance_id = watering_data.balance_id
                JOIN plants ON plants_to_balance.plant_id = plants.plant_id
                WHERE plants.experiment_id = '{0}';
        """

    print(get_water.format('E_001'))
    print(experiment_id)
    water_data = pd.read_sql(get_water.format(experiment_id), conn)
    return water_data


def get_watering_history(balance_id, num_days=7, experiment_id='W030'):
    """
    This will get the most recent readings for a particular balance
    using num_days to denote how far back to check readings
    """
    conn = create_connection('gravi')
    with conn.cursor() as cursor:

        sql = "SELECT plants_to_balance.plant_id, logdate, start_weight, end_weight, status, experiment_id \
        FROM watering_data\
        JOIN plants_to_balance\
        ON plants_to_balance.balance_id = watering_data.balance_id \
        AND plants_to_balance.start_date <= watering_data.logdate AND (end_date >= watering_data.logdate OR end_date IS NULL) \
        WHERE plants_to_balance.balance_id = {0} \
        AND logdate >= CURDATE() - {1} AND experiment_id = '{2}'".format(
            balance_id, num_days, experiment_id)

        water_data = pd.read_sql(sql.format(balance_id, num_days, experiment_id),
                                 conn)
        return water_data


def get_balance_history(balance_id, num_days=7):
    """
    This will get the most recent readings for a particular balance
    using num_days to denote how far back to check readings
    """

    conn = create_connection('gravi')
    with conn.cursor() as cursor:

        sql = "select logdate, weight from balance_data \
        where balance_id = {0} \
        and logdate > CURDATE()-{1};".format(balance_id, num_days)

        water_data = pd.read_sql(sql,
                                 conn)
        return water_data


def get_experiments():
    try:
        conn = create_connection('gravi')
        with conn.cursor() as cursor:
            sql = 'select * from experiment'
            result = pd.read_sql(sql, conn)
            return result
    except:
        print('Couldn\'t get experiments')
        return ''

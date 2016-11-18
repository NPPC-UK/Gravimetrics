#!/usr/bin/python3

""""Program to run on gravimetrics, that given parameters
will either record data or else water the plants

Data recorded will be stored in a database through this script and the
lower level readings will be done
By a small C program which will also be called through this script!

Author: Nathan Hughes (nah31@aber.ac.uk | nathan1hughes@gmail.com)

Dependancies:

 1. python3
 2. pymysql


Program flow

1. Get plant watering data from SQL database
2. Check which plants this particular Pi is assigned to, from the database
3. Create a data container for the plants read from the database
4. Perform either reading/watering functions
5. Create a buffer to wait between each reading
6. Perform database updates
7. Clean up and stop

"""

import sys
from socket import gethostname
from getopt import getopt, GetoptError
from subprocess import Popen, PIPE, STDOUT
from database import Connection


# Few functions just for tidiness
def print_help():
    """Prints the help message"""
    print("The usage of this program is: \n"
          "python3 gravi.py\n"
          "-w (to water)\n"
          "-t (to run testing mode)\n")


def print_plants(plants):
    """This prints every plants object found"""
    for plant_object in plants:
        print(plant_object)


def perform_reading_update(plant, connection, is_watering):
    """Takes a plant and gets a reading based on its attributes;
    updates balance DB if not watering"""
    cmd = "gravi_util  Balance " + str(plant.get_balance())
    output = Popen((cmd), shell=True,
                   stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().decode()
    plant.set_start_weight(output if output.isdigit() else 0)
    # if not watering then perform the database update
    if not is_watering:
        connection.perform_weight_update(plant)


def perform_watering_update(plant, connection):
    """Takes a plant and waters to weight based on its attributes; updates the watering DB"""
    cmd = "gravi_util water " + plant.get_balance() +\
        " " + plant.get_solenoid() + " " + str(plant.get_target_weight())
    output = Popen((cmd), shell=True,
                   stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().decode()
    # if the weight could not be captured then set weight to 0
    plant.set_end_weight(output if output.isdigit() else 0)
    connection.perform_watering_update(plant)


def process_args():
    """Processes the command-line arguments and returns a dict with connection information"""
    try:
        options, values = getopt(sys.argv[1:], 'wthH:U:P:D:')
    except GetoptError as err:
        print('Argument error: ', err)
        print('What is this!: ', values)
        sys.exit(1)

    arguments = {}
    for opt, arg in options:
        if opt in '-w':
            print("Watering Mode Activated")
            arguments['watering_mode'] = True
        elif opt in '-t':
            print("Testing Mode Activated")
            arguments['testing_mode'] = True
        elif opt in '-h':
            print_help()
            sys.exit(0)
        elif opt in '-H':
            arguments['host'] = arg
        elif opt in '-U':
            arguments['user'] = arg
        elif opt in '-P':
            arguments['password'] = arg
        elif opt in '-D':
            arguments['database'] = arg
        else:
            print("Unsure of argument: ", arg)

    return arguments


def main():
    """This is the main entry point for the program to control gravimetrics """

    arguments = process_args()

    # Double check all data has been correctly set
    if 'host' not in arguments or\
       'user' not in arguments or\
       'password' not in arguments or\
       'database' not in arguments:
        print("Error setting database credentials")
        print(arguments)
        sys.exit(1)

    connection = Connection()
    connection.create_connection(arguments['host'], arguments['user'],
                                 arguments['password'], arguments['database'])

    # If we're testing use the pi name test,
    # else we just wanna use the host name
    plants = connection.get_plants(
        gethostname() if not arguments['testing_mode'] else "test")

    # If the retrieval
    if plants is None:
        sys.stderr.write("No plant information found\nCheck connection\n")
        sys.exit(1)

    for plant in plants:

        print(plant)

        # Get the current balance
        perform_reading_update(
            plant, connection, True if 'watering_mode' in arguments else False)

        # If watering mode is activated then perform some watering
        if 'watering_mode' in arguments:
            perform_watering_update(plant, connection)

        if 'testing_mode' in arguments:
            print(plant)

if __name__ == "__main__":
    main()

#!/usr/bin/python3
# pylint: disable-msg=invalid-name

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
q4. Perform either reading/watering functions
5. Create a buffer to wait between each reading
6. Perform database updates
7. Clean up and stop

"""

import sys
from getopt import getopt, GetoptError
from subprocess import Popen, PIPE, STDOUT
from re import search
from time import sleep
from database import Connection


def print_help():
    """Prints the help message"""
    print("To use this program you need to run the following:\n\
    ./gravi.py -H <host name> -U <user> -P <password> -D <database to use>\
    -R <Pi number> <-w is optional if you want to water> ")


def find_value(output_str):
    """Finds a value from a string"""
    if output_str is not None:
        return search(r'\d+', output_str).group()
    else:
        return 'NULL'


def perform_lifting(pi, arduino, ld):
    """ Lifts or drops the balance """

    print("I was given ld of: {0}".format(ld))
    
    cmd = 'ssh -T pi@gravi0{0} gravi_utils-dev lifter {1} {2}'.format(
        pi, arduino, ld)

    print('Calling lifting: {0}'.format(cmd))

    output = Popen((cmd), shell=True, stdin=PIPE, stdout=PIPE,
                   stderr=STDOUT, close_fds=True).stdout.read().decode()

    print(str(output))

    # This will sleep for 5 seconds and allow the lifter time to work and
    # balance time to steady/reset.
    sleep(5)


def validate_output(output_str):
    """This function returns true if the string given is a suitable value
    from interacting with gravi_utils"""
    errors = ['Could not resolve hostname', 'not found',
              'Error writting to device', 'Timeout error']

    if any(error in output_str for error in errors):
        return False
    else:
        return True


def print_plants(plants):
    """This prints every plants object found"""
    for plant_object in plants:
        print(plant_object)


def perform_reading_update(pi, plant, connection, is_watering):
    """Takes a plant and gets a reading based on its attributes;
    updates balance DB if not watering"""
    
    # Bit of quick hacky logic for prototyping lifters here:
    if pi == '8':
        print("Accepted?")
        perform_lifting(
            pi, '/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_754333035313515032A1-if00', 'd')

    cmd = "ssh -T pi@gravi0{0} gravi_utils balance {1} 2>&1 ".format(
        pi, plant.get_load_cell())

    print("The command used to get this reading was: {0}".format(cmd))
    output = Popen((cmd), shell=True,
                   stdin=PIPE, stdout=PIPE,
                   stderr=STDOUT,
                   close_fds=True).stdout.read().decode()

    print("The output of this reading is: {0}".format(output))
    plant.set_start_weight(find_value(
        output) if validate_output(output) else 'NULL')
    # if not watering then perform the database update
    if is_watering:
        perform_watering_update(pi, plant, connection)
    else:
        connection.perform_weight_update(plant)

    # Bit of quick hacky logic for prototyping lifters here:
    if pi == '8':
        perform_lifting(
            pi, '/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_754333035313515032A1-if00', 'l')


def perform_watering_update(pi, plant, connection):
    """Takes a plant and waters to weight based on its attributes; updates the watering DB"""

    # quick and dirty fix for now, if first reading failed
    if plant.get_start_weight() == 'NULL' or not str(plant.get_start_weight()).isdigit():
        perform_reading_update(pi, plant, connection, False)
        if plant.get_start_weight() == 'NULL' or not str(plant.get_start_weight()).isdigit():
            return 1  # no point watering if we can't read properly

    if plant.get_start_weight() >= plant.get_target_weight():
        print("Plant needs no water: Current: {0} Target: {1}".format(
            plant.get_start_weight(), plant.get_target_weight()))
        plant.set_end_weight(plant.get_start_weight())
    else:
        activate_master(1, ((int(plant.get_balance()) - 1) // 8) + 1)
        cmd = "ssh -T pi@gravi0{0} gravi_utils water {1} {2} {3} 2>&1".format(
            pi, plant.get_load_cell(), plant.get_solenoid(), plant.get_target_weight())
        print(cmd)
        output = find_value(Popen((cmd), shell=True,
                                  stdin=PIPE, stdout=PIPE,
                                  stderr=STDOUT,
                                  close_fds=True).stdout.read().decode())
        # if the weight could not be captured then set weight to 0
        plant.set_end_weight(output if validate_output(output) else 'NULL')
        activate_master(0, ((int(plant.get_balance()) - 1) // 8) + 1)

    connection.perform_watering_update(plant)


def get_master_pin(bench_num):
    """This returns the master pin for a bench"""
    master_pins = {1: 14, 2: 15, 3: 18, 4: 23, 5: 24, 6: 25, 7: 8,
                   8: 7, 9: 9, 10: 11, 11: 5, 12: 6, 13: 13, 14: 19, 15: 26}
    return master_pins[int(bench_num)]


def activate_master(off_on, plant_position):
    """This turns on/off the master solenoid for that particular plant's bench
    takes the plants position and a Boolean off_on to decide which solenoid to activate"""
    cmd = "gravi_utils master /sys/class/gpio/gpio{0}/value {1}".format(
        get_master_pin(plant_position), off_on)
    print(cmd)
    Popen((cmd), shell=True,
          stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().decode()


def process_args():
    """Processes the command-line arguments and returns a dict with connection information"""
    try:
        options, values = getopt(sys.argv[1:], 'wthH:U:P:D:R:')
    except GetoptError as err:
        print('Argument error: ', err)
        print('What is this!: ', values)
        sys.exit(1)

    # some defaults set to prevent errors
    arguments = {'watering_mode': False, 'testing_mode': False}
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
        elif opt in '-R':
            arguments['pi'] = arg
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
        arguments['pi'] if not arguments['testing_mode'] else "1")

    # If the retrieval
    if plants is None:
        sys.stderr.write("No plant information found\nCheck connection\n")
        sys.exit(1)

    for plant in plants:
        perform_reading_update(arguments['pi'], plant, connection,
                               arguments['watering_mode'])
        
    print("| SUMMARY OF BENCH {0}".format(arguments['pi']))
    for plant in plants:
        print(plant)

        
if __name__ == "__main__":
    main()

#!/usr/bin/python3

import csv
from subprocess import Popen, PIPE, STDOUT

commands = []
results = []

with open('Balances.txt', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    balance_id = 1
    for usb in reader:
        pi_to_use = 'gravi0' + str((balance_id - 1) // 16 + 1)
        address_to_use = usb[1]
        command = "ssh nathan@gravimetrics.ibers ssh pi@" + \
            pi_to_use + ' gravi_utils balance ' + '/dev/serial/by-id/' + \
            address_to_use

        commands.append(command)
        balance_id += 1

balance_id = 1
for cmd in commands:
    result = {}
    output = Popen((cmd), shell=True, stdin=PIPE,
                   stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().decode()
    result['balance_id'] = balance_id
    result['response'] = output
    results.append(result)
    balance_id += 1

    print("Balance {0} is at {1}".format(
        result['balance_id'], result['response']))


with open('results.txt', 'w+') as file:
    for item in results:
        file.write(str(item['balance_id']) + ' : ' +
                   (str(item['response']).replace('\n', '')) + '\n')

"""
Little quick script for populating a sql insert statement for all the balances
replace the word "test." with whatever schema is being used
"""
import csv

with open('Balances.txt', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    statement = "INSERT INTO test.balances(balance_id, cable_id, address, pi_assigned)VALUES\n"
    balance_id = 1
    for row in reader:
        statement += ("(\"" + str(balance_id) + "\",\"" +
                      str(balance_id - (16 * ((balance_id - 1) // 16))) + "\", \"" + row[1] + "\",\"" +
                      str(((balance_id - 1) // 16) + 1) + "\"),\n")
        balance_id += 1

    statement = (statement[::-1].replace(',', ';', 1))[::-1]

    print(statement)

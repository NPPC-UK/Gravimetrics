#!/bin/bash

#####################################################
# This little script just scans all in the	    #
# location the balances are found		    #
# and checks their weight the names of the	    #
# files bear no relation of what the		    #
# actual balance is, just the output for debugging  #
#####################################################



count=0
for f in /dev/serial/by-id/*; do
    gravi_utils balance $f >> balance_$count.txt 2>&1
    (( count++ ))
done
echo Done! 

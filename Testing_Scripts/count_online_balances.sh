#!/bin/bash

#This gets the number of balances showing to be plugged in to each pi

for pi in {1..6}; do
    echo "Checking Gravi0$pi"
    ssh nathan@gravimetrics.ibers ssh pi@gravi0$pi ls /dev/serial/by-id/ | wc -l
done


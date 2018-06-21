#!/bin/bash

dbinfo_file="dbinfo.dat"

read -p "Enter DB User: " usr
read -p "Enter DB Host: " host
read -p "Enter DB Name: " db
read -s -p "Enter DB Password: " pswd

echo $usr >> $dbinfo_file
echo $host >> $dbinfo_file
echo $db >> $dbinfo_file
echo $pswd >> $dbinfo_file

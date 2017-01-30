#!/bin/bash

apply_script(){
    mysql -hvenom.ibers -ugravi -p$2 < $1
}

echo "Enter User Gravi Password: "
read gravi_pass

apply_script MYSQL_Testing_Setup.sql $gravi_pass
apply_script MYSQL_Testing_Data.sql $gravi_pass

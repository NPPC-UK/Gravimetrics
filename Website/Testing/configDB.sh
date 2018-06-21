#!/bin/bash

apply_script(){
    mysql -hvenom.ibers -ugravi -p$2 < $1
}

echo "Enter User Gravi Password: "
read gravi_pass

apply_script setupDB.sql $gravi_pass
apply_script populateDB.sql $gravi_pass

#! /bin/bash
# This bash script takes either 1 or 2 arguments
# the first is an indication of which test to run
# the second is an optional value for the end weight to be echoed 
#

# Function to create two testing terminals
# 
create_terminals(){
    # Open up the two ports called testing0 and testing1 
    socat -d -d pty,raw,echo=0,link=/tmp/testing0 pty,raw,echo=0,link=/tmp/testing1 &
    
} &> /dev/null


# This function builds the program and outputs the to the log file
build(){

    scan-build make -C ../
    printf '=%.0s' {1..25}
    printf '\n' 
    make -C ../     
    
} &> build.log

# Function to test watering
# @param $1 is the initial value
# @param $2 is the target weight
# @param $3 is the end weight (must be greater than $3 or something is wrong)
# You will want to keep $2 and $3 the same value, unless
# testing to see how the program handles a scale/valve freezing
test_watering(){

    create_terminals # open the testing terminals 

    sleep 2
    
    #Run watering program

    valgrind >> valgrind.log  ../gravi_utils water /tmp/testing0 /tmp/testing0 $2 >> Gravi_Utils.log 2>&1 &

    #Let the program catch up with opening socat
    sleep 2

    # Check for input, this will end up being the initial weight 
    if [ -z ${2+x} ]; then 
	#push the input back to the program 
	echo "testS9999g" > /tmp/testing1
    else
	echo $2 > /tmp/testing1
    fi
    
    echo $3 > /tmp/testing1 # echoing the end weight 
     
    #catch up time 
    sleep 1 

    killall socat #clean up by killing all instances of socat

   # (1>&2 cat valgrind.txt) # echo out the valgrind output to sterr to keep separated from stdout
}

# Function to test balance reading 
test_balance(){
    # Give this time to catch up with socat
    sleep 2

    # run the program to test
    valgrind >> valgrind.log ../gravi_utils balance /tmp/testing0 >> Gravi_Utils.log 2>&1 &
    
    #wait for a second to let the request to be sent
    sleep 2
    
    # output a random int back to the program
    echo $1  > /tmp/testing1

    sleep 1
    }



######################Setup, Build and static analysis############
rm Gravi_Utils.log valgrind.log  build.log 2> /dev/null
build

###########################Tests################################
test_watering 100 200 200 > test.log # Normal test, should work with an output of 200
test_watering 500 300 500 >> test.log # Plant above weight, should finish with output of 500
test_watering abc def hgh >> test.log # Test should fail as no sensible values are being passed

sleep 2
echo "====" >> test.log

test_balance "ab   cd100g" >> test.log # Normal input
test_balance eha2020g >> test.log # Normal input
test_balance aksdalsd >> test.log # Should report 0 and give some stderr

##########################Output displaying#########################
sleep 5 # just sleep to make sure all child processes catch up and die

cat build.log 

cat Gravi_Utils.log | grep -B4 "ERROR"

#cat Gravi_Utils.log 

# Print finished message (commented out for now as it interferes with the python testing 
echo -e  Done!  



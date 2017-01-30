/**
 * @file main.c
 * @author Nathan Hughes
 * @date 25/8/2016
 * @brief Program to interact with scales and solenoids
 *
 * This program uses C to interact with the hardware in 
 * gravimetrics, using standard C commands that will compile 
 * on most systems, although aimed primarily for the Raspberry Pi
 *
 * @see https://support.plant-phenomics.ac.uk:8081/nah31/Gravi_Utils/
 * @bug No known issues 
 */
#include "gravi_utils.h"

/**
 * @brief Main entry point for the program
 *
 * Takes in a variable number of arguments that can be seen with the "help" command 
 *
 * @param argc the number of arguments given 
 * @param argv the strings passed as arguments details can be found by running Gravi_Utils help
 * @return exit code 
 *
 */
int main(int argc, char *argv[]) {
  
  if(unlikely(argc < 2)) {
    fprintf(stderr, "Not enough arguments, please state either balance or water with other required information\n");
    return 0;
  }
  else if(argc >= 2 && argc < 5){
    if(!strcmp(argv[1], "help")){
      
      printf("The usage of this program is as follows: "
	     "\nArg 1 can be either \'balance\' or else \'water\' "
	     "\nArg 2 is the balance port address "
	     "\nArgs 3 is used only if watering and is the GPIO address"
	     "\nArg 4 is also only used for watering and is the target weight as an integer value\n" );
      return 0;    
    }
    if(!strcmp(argv[1], "balance")){
      
      /*
       * This is the output to stdout
       */
      printf("%d\n",get_balance(argv[2]));
      exit(EXIT_SUCCESS);
    }

    else if (!strcmp(argv[1], "master")){
	activate_master_solenoid(argv[2], argv[3][0]);
	exit(EXIT_SUCCESS);
      }
    else if (!strcmp(argv[1], "lifter")){
      lift(argv[2], argv[3][0]);
    }
    else if (!strcmp(argv[1], "tare")){
      tare_balance(argv[2]);
    }
    else if (!strcmp(argv[1], "test_gpio")){
      if(interact_with_port(argv[2], 'W', argv[3][0])){
	printf("Sucessfully applied action %c on: %s",  argv[3][0], argv[2]);
	exit(EXIT_SUCCESS);
      }else{
	fprintf(stderr, "Error running the testing script!");
	exit(EXIT_FAILURE);
      }
      
    }
    
    else {
      fprintf(stderr, "Need additional information, contact system administrator\n");
      exit(EXIT_FAILURE);
    }
  }
  
  if (argc == 5 && !strcmp(argv[1], "water")){
    
    /*
     * This is the actual magic being called and printed to the stdin
     */
    printf("%d\n", water_to_weight(argv[2], argv[3], atoi(argv[4])));
    
    exit(EXIT_SUCCESS); 
  }
  else{
    fprintf(stderr, "Something went wrong with the watering\n");
    exit(EXIT_FAILURE);
  }
  return 0; // I can't imagine a condition where this is actually triggered! 
}


/**
 *
 * Function implementations 
 *
 */
int get_balance(char* balance_port_id){
  return interact_with_port(balance_port_id, 'B', 0);
}

int water_to_weight(char* balance_PortID, char* water_port_id, int target_weight){

  int current = get_balance(balance_PortID);
  
  if(current < target_weight){

    /*
     * Start some clocking information
     */
    time_t elapsed = 0, start =time(NULL);
    int tries = 0;
    
    while (interact_with_port(water_port_id, 'W', '1') < 0 && tries < PORTATTEMPTS) // turn water on
      tries++; 

    int initial = get_balance(balance_PortID);
    
    while(current < target_weight && elapsed < WATERTIMEOUT ){
      //wait for watering to be complete
      current = get_balance(balance_PortID);
      elapsed = (time(NULL) - start);

      // if after 10seconds no water appears then something has gone wrong
      if (current == initial && elapsed > WATERCHANGETIMEOUT)
	break;
    }
    
    tries = 0; 
    while (unlikely(interact_with_port(water_port_id, 'W', '0') <  0) && tries < PORTATTEMPTS)
      fprintf(stderr, "Error turning off water\n"); // turn water off
  }
  //wait here as it would increase accuracy of the watering update if we let water settle
  sleep(5);
  return get_balance(balance_PortID);
}


int interact_with_port(char* port_id, char BWLT, char off_on){

  /*
   * Just to clarify: BW, B will refer to balance whilst W refers to watering, and L the lifter 
   */
  speed_t baud = B9600; // baud rate
  int fd = open(port_id, (BWLT == 'B' || BWLT == 'L' || BWLT == 'T') ? O_RDWR : O_WRONLY); //Open the port with the correct RW settings

  struct termios settings; // structure for the settings that will be used for the port 
  tcgetattr(fd, &settings);
  
  cfsetospeed(&settings, baud); // baud rate 
  settings.c_cflag &= ~PARENB; // no parity 
  settings.c_cflag &= ~CSTOPB; // 1 stop bit 
  settings.c_cflag &= ~CSIZE; // Specify the size of   
  settings.c_cflag |= CS8 | CLOCAL; // 8 bits 
  settings.c_lflag = ICANON; // canonical mode 
  settings.c_oflag &= ~OPOST; // raw output 
  tcsetattr(fd, TCSANOW, &settings); // apply the settings 
  tcflush(fd, TCOFLUSH); // Discard useless info 
  fcntl(fd, F_SETFL, 0); // apply file control operations 

  // Initialise file descriptor sets
  fd_set read_fds, write_fds, except_fds;
  FD_ZERO(&read_fds);
  FD_ZERO(&write_fds);
  FD_ZERO(&except_fds);
  FD_SET(fd, &read_fds);

  // Set timeout to 3.0 seconds
  struct timeval timeout;
  timeout.tv_sec = PORTTIMEOUT; // Read timeout defined in header, any more than this and something has went wrong
  timeout.tv_usec = PORTTIMEOUT;
  
  int w = 0;
  if(BWLT == 'W'){
    w = (int)  write(fd, &off_on, 1); 
  }
  else if (BWLT == 'L'){
    w = (int) write(fd, (off_on) ? "d": "l" , 1); // if off == True then drop else lower 
  }
  else if (BWLT == 'T'){
    w = (int) write(fd, "t", 1); // send tare signal 
  }
  else{
    w = (int) write(fd, "w", 1); // writes to the port a w or a 1/0 depending on function 
  }
  
  //If there's an error in writing to the scales then tell us!
  if(unlikely(w < 0) && BWLT != 'L'){
    fprintf(stderr, "Error writting to device: %s\n", port_id);
    return -1; 
  }

  //If we flip switch to water then return as it's worked
  if(BWLT == 'W') return w;
  else if (BWLT == 'L') return w; 

  
  // Wait for input to become ready or until the time out; the first parameter is
  // 1 more than the largest file descriptor in any of the sets
  if (likely(select(fd + 1, &read_fds, &write_fds, &except_fds, &timeout) == 1)) {
    
    //This buffer holds the data from the serial port
    char buffer[BUFFERSIZE]; //Could reduce this to around 18 in length but better to have more buffering room

    // fd is ready for reading
    uint8_t n = (uint8_t) read(fd, buffer, sizeof(buffer));  //Reads the length of the serial data

    buffer[n] = 0;
    
    if(deblank(buffer)) fprintf(stderr, "Error getting data from scales") ; // remove all unhappy characters from the input

    close(fd); // close the connection

    return atoi(buffer); // convert the result to a number and cast to be short
  }
  else
    fprintf(stderr, "Timeout error\n");
  return 0; // timeout or error
}

int activate_master_solenoid(char* port_id, char off_on){
  return  interact_with_port(port_id, 'W', off_on);
}

int deblank(char* input){
  
  char isNumerical = 0;

  for(int i = 0, j = 0; i < (int)strlen(input); i++, j++){

    /* This additional check looks for numbers within the given string
     * if no numbers are present we will return 0 indicating a failure 
     * in finding useful data. 
     */ 
    if (isNumerical != 0 && isdigit(input[i])) isNumerical = 1;  
    
    if(input[i] >= '0' && input[i] <= '9'){
      input[j] = input[i];
    } 
    else{
      j--;
    }
  }
  return isNumerical; 
}

int lift(char* lifter_address, char lift_drop){

  interact_with_port(lifter_address, 'L', (lift_drop == 'l') ? 0 : 1); 
  
  return 0; 
}

int tare_balance(char* balance_address){
  interact_with_port(balance_address, 'T', 0);
  return 0; 
}

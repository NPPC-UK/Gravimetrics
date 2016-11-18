#/**
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
      fprintf(stderr, "Need additional information, please give port file and/or watering target\n");
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

    clock_t start = clock(); // start the clock
    int elapsed_time = 0; 
    interact_with_port(water_port_id, 'W', '1'); // turn water on

    while(current < target_weight || elapsed_time >= WATERTIMEOUT ){
      //wait for watering to be complete
      current = get_balance(balance_PortID);
      clock_t diff = clock() - start;
      elapsed_time = (diff * 1000 / CLOCKS_PER_SEC) / 1000; 
      
    }
    if (unlikely(interact_with_port(water_port_id, 'W', '0') < 0)) fprintf(stderr, "Error turning off water\n"); // turn water off
  }
  return get_balance(balance_PortID);
}


int interact_with_port(char* port_id, char BW, char off_on){

  speed_t baud = B9600; // baud rate
  int fd = open(port_id, (BW == 'B') ? O_RDWR : O_WRONLY); //Open the port with the correct RW settings

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
  if(BW == 'W'){
    w = (int)  write(fd, &off_on, 1); 
  }else{
    w = (int) write(fd, "w", 1); // writes to the port a w or a 1/0 depending on function 
  }
  
  //If there's an error in writing to the scales then tell us!
  if(unlikely(w < 0))
    fprintf(stderr, "Error writting to device: %s\n", port_id);

  //If we flip switch to water then return as it's worked
  if(BW == 'W') return w;

  
  // Wait for input to become ready or until the time out; the first parameter is
  // 1 more than the largest file descriptor in any of the sets
  if (likely(select(fd + 1, &read_fds, &write_fds, &except_fds, &timeout) == 1)) {
    
    //This buffer holds the data from the serial port
    char buffer[BUFFERSIZE]; //Could reduce this to around 18 in length but better to have more buffering room

    // fd is ready for reading
    uint8_t n = (uint8_t) read(fd, buffer, sizeof(buffer));  //Reads the length of the serial data

    buffer[n] = 0;
    
    if(deblank(buffer)) fprintf(stderr, "error getting data from scales") ; // remove all unhappy characters from the input

    close(fd); // close the connection

    return atoi(buffer); // convert the result to a number and cast to be short
  }
  else
    fprintf(stderr, "Timeout error\n");
  return 0; // timeout or error
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



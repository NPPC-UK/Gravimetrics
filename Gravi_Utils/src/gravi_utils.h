#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <sys/select.h>
#include <stdint.h>


#define WATERTIMEOUT 100
#define WATERCHANGETIMEOUT 10
#define PORTATTEMPTS 3
#define PORTTIMEOUT 5
#define BUFFERSIZE 18

/**
 * @see https://kernelnewbies.org/FAQ/LikelyUnlikely
 * @issue cannot use the linux include as gcc doesn't have the specific kernel included in search
 * These defines help to guess which outcomes are usually expected from conditionals
 * for this I am assuming that most of the time this software will work
 * that lets the compiler optimise a little better
 */
#define likely(x)       __builtin_expect(!!(x), 1)
#define unlikely(x)     __builtin_expect(!!(x), 0)

/**
 * @brief Gets the balance of a particular port
 * @param Balance_port_id the address of the port to examine
 * @return The weight in grams 
 */
int get_balance(char* balance_port_id);

/**
 * @brief Waters to the target weight
 *
 * This function waters a specific plant pot to the target weight given
 * 
 * @param balance_port_id the address of the serial port to read for watering
 * @param water_port_id the id of the solenoid to use when allowing water
 * @param target_weight of a plant 
 * @return the weight of the plant at the end of the watering
 */
int water_to_weight(char* balance_port_id, char* water_port_id, int target_weight);


/**
 * @brief Reads/Sets the value of either a water solenoid or a balance 
 *
 * Making use of the params given it decides what it should do to a port address given
 * this function will either apply a watering action or a weight reading action 
 * either way it returns a value which indicates the weight/exit code of its process 
 * 
 * @param port_id the address of the port file 
 * @param BWLT an indication of whether to water or read balance or lift or tare
 * @param off_on indication to write a high or low to the port (used for watering solenoids)
 * @return Either the exit code, or the value of a read balance 
 */
int interact_with_port(char* port_id, char BWLT, char off_on);


/**
 * @brief Used to flipping master solenoids =
 *
 * This makes it easier to interact with master solenoids for controllers.
 *
 * @param port_id the address to activate
 * @param off_on indication to write a high or low value for the solenoid
 * @return exit code of the program 
 */
int activate_master_solenoid(char* port_id, char off_on); 

/**
 * @brief Function to remove bad output from a string  
 *
 * String given to this function should be just numbers, this function ensures that 
 * no garbage characters pollute the output of the scales
 *
 * @param input char array pointer that needs cleaned up
 * @return Either 0 or 1 indicating if the given input contained any useful numerical data
 */
int deblank(char* input);


/**
 * @brief This will lift or drop the stepper motors on a balance
 *
 * Given a character input will decide to send a lift or a drop signal 
 * to the lifter associated to that balance
 *
 * @param lifter_address the address to push the signal to 
 * @param lift_drop indicates to lift or drop the lifter 
 * @return Either 0 or 1 indicating success or failure of signal reception
 */
int lift(char* lifter_address, char lift_drop); 

/**
 * @brief This will tare a balance
 * 
 * Takes a balance address and sends a signal to trigger it to tare itself
 * 
 * @param the address of the balance serial 
 * @return 1 or a 0 exit code
 */
int tare_balance(char* balance_address);

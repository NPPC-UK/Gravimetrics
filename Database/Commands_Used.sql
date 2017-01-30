/* 

  This file is made to hold a few of the more interesting statements used to manipulate 
  the database of gravimetrics 
*/


-- This command will grab all of the plant_id's along with which USB address to use and GPIO for watering
-- and target weight
SELECT fourth.plant_id, second.balance_id, address, gpio_pin, target_weight FROM balances as first
  inner join plants_to_balance as second
    on first.balance_id = second.balance_id
  inner join watering_valves as thrid
    on thrid.balance_id = second.balance_id
  inner join plants as fourth
    on fourth.plant_id = second.plant_id
    WHERE second.end_date IS NULL OR second.end_date > curdate() AND first.pi_assigned = 'testPi';

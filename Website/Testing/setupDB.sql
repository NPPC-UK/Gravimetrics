/*
  Be wary this script will delete all current data in the db
  Also there may be an issue with the ordering of the delete
*/

use test;  /*Use the testing database*/

drop table if exists watering_valves;
drop table if exists plants_to_balance;
drop table if exists balance_data;
drop table if exists plants;
drop table if exists watering_data;
drop table if exists experiment;
drop table if exists balances;
drop table if exists hosts;
drop table if exists dates;

/*
 This table holds data on a given experiment being hosted on gravimetrics
 Primary Key: id = the identification of the experiment
*/
CREATE TABLE experiment(
  experiment_id VARCHAR(30) NOT NULL ,
  start_date DATETIME NOT NULL ,
  end_date DATETIME NOT NULL ,
  owner VARCHAR(30) NOT NULL,
  UNIQUE KEY start_date (start_date),
  UNIQUE KEY end_date (end_date),
  PRIMARY KEY (experiment_id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*
 This is the host table for information about the Pi's themselves
 Primary Key = Hostname of the actual Pi
TODO: Consider removing hosts table if un-used

*/
CREATE TABLE hosts (
  host_name INT(2) NOT NULL UNIQUE,
  PRIMARY KEY (host_name)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


/*
 This table holds the data from the physical balances' RS232 connections
*/
CREATE TABLE balances (
  balance_id INT(3) NOT NULL UNIQUE,
  cable_id INT(3) NOT NULL,
  address  VARCHAR(100),
  pi_assigned INT(2),
  FOREIGN KEY (pi_assigned) REFERENCES hosts(host_name),
  PRIMARY KEY (balance_id)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*
  This holds the information about the watering valves GPIO
*/
CREATE TABLE watering_valves(
  balance_id INT(3) NOT NULL UNIQUE,
  gpio_pin VARCHAR(30) NOT NULL,
  FOREIGN KEY (balance_id) REFERENCES balances(balance_id),
  PRIMARY KEY (balance_id)

) ENGINE=InnoDB DEFAULT CHARSET=latin1;


/*
 This table holds all of the balance readings for Gravi
 Primary Key: (balance_id, logdate, weight) = all of these together give a unique row
 TODO: PLANTS RATHER THAN BALANCE_ID
*/
CREATE TABLE balance_data (
  balance_id INT(3) NOT NULL ,
  logdate DATETIME NOT NULL,
  weight INT(11),
  experiment_id VARCHAR(30) NOT NULL,
  target_weight INT(11) NOT NULL,
  FOREIGN KEY (experiment_id) REFERENCES experiment(experiment_id),
  FOREIGN KEY (balance_id) REFERENCES balances(balance_id),
  PRIMARY KEY (balance_id, logdate)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*
  THIS BE THE PLANTS TABLE
  It needs integrated with the actual main database to track all of the useful stuff
  The target_weight in here is only the *current* target weight, targets are also recorded in
  the balance_data and the watering_data table!
*/
CREATE TABLE plants (
  plant_id VARCHAR(30) NOT NULL ,
  experiment_id VARCHAR(30) NOT NULL,
  target_weight INT(11) NOT NULL,
  FOREIGN KEY (experiment_id) REFERENCES experiment(experiment_id),
  PRIMARY KEY (plant_id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


/*
  Linker between the plants and the balances
*/
CREATE TABLE plants_to_balance(
  start_date DATETIME NOT NULL,
  end_date DATETIME NOT NULL,
  plant_id VARCHAR(30) NOT NULL,
  balance_id INT(3) NOT NULL,
  FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
  FOREIGN KEY (balance_id) REFERENCES balances(balance_id),
  PRIMARY KEY(start_date, end_date, plant_id, balance_id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*
 This table holds the data about what has been watered, when and any issues created
*/
CREATE TABLE watering_data (
  balance_id INT(3) NOT NULL,
  logdate DATETIME NOT NULL,
  start_weight INT(11) NOT NULL,
  end_weight INT(11) NOT NULL,
  status VARCHAR(5) NOT NULL,
  experiment_id VARCHAR(30) NOT NULL,
  target_weight INT(11) NOT NULL,
  FOREIGN KEY (balance_id) REFERENCES balances(balance_id),
  FOREIGN KEY (experiment_id) REFERENCES experiment(experiment_id),
  PRIMARY KEY (balance_id, logdate)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



/*
  This shows the tables and their relationships so the user can see what has been done by this script
*/

SHOW tables;

SELECT
  `TABLE_SCHEMA`,                          -- Foreign key schema
  `TABLE_NAME`,                            -- Foreign key table
  `COLUMN_NAME`,                           -- Foreign key column
  `REFERENCED_TABLE_SCHEMA`,               -- Origin key schema
  `REFERENCED_TABLE_NAME`,                 -- Origin key table
  `REFERENCED_COLUMN_NAME`                 -- Origin key column
FROM
  `INFORMATION_SCHEMA`.`KEY_COLUMN_USAGE`  -- Will fail if user don't have privilege
WHERE
  `TABLE_SCHEMA` = SCHEMA()                -- Detect current schema in USE
  AND `REFERENCED_TABLE_NAME` IS NOT NULL; -- Only tables with foreign keys


/*
Use this syntax to insert if not exists

insert into experiment( id, start_date, end_date, owner)
SELECT * FROM (SELECT "1", 20160801, 20161201, "Dr Test") AS tmp
WHERE NOT EXISTS (
    SELECT id FROM experiment WHERE id = 1
) LIMIT 1;
/*

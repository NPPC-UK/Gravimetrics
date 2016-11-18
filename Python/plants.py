"""Classes with data on plants"""


class Plants(object):

    # pylint: disable-msg=too-many-instance-attributes
    """Class to act as a container for plant data"""

    def __init__(self, plant_id, balance, address,
                 solenoid, target_weight, experiment_id):
        """Initialisation function to set all of the required variables"""
        self.balance = balance
        self.plant_id = plant_id
        self.address = address
        self.solenoid = solenoid
        self.target_weight = target_weight
        self.experiment_id = experiment_id
        self.start_weight = None
        self.end_weight = None
        self.status = None

    def __str__(self):
        return "| Plant: " + self.plant_id + " Balance: " + \
            str(self.balance) + "| Experiment ID: " + self.experiment_id +\
            "| Target Weight: " + str(self.target_weight) + " |"

    def get_balance(self):
        """Gets the balance_id of this plant"""
        return self.balance

    def get_load_cell(self):
        """Gets the load cell address"""
        return self.address

    def get_solenoid(self):
        """Gets the solenoid address"""
        return self.solenoid

    def set_start_weight(self, start_weight):
        """Sets the weight before watering"""
        self.start_weight = start_weight

    def get_start_weight(self):
        """Gets the start weight of a plant"""
        return self.start_weight

    def set_end_weight(self, end_weight):
        """Sets the end weight of a plant after watering"""
        self.end_weight = end_weight

    def get_end_weight(self):
        """Gets the end weight of a plant after watering"""
        return self.end_weight

    def get_target_weight(self):
        """Gets the target weight of a plant"""
        return self.target_weight

    def get_status(self):
        """Gets the status of watering"""
        return self.status

    def set_status(self, status):
        """Sets a status indicating how the watering went"""
        self.status = status

    def get_experiment_id(self):
        """Gets the experiment id"""
        return self.experiment_id

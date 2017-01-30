"""Classes with data on plants"""


class Plants(object):

    # pylint: disable-msg=too-many-instance-attributes
    # pylint: disable-msg=too-many-arguments
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
        self.start_weight = 'NULL'
        self.end_weight = 'NULL'
        self.status = 0  # default to 0

    def __str__(self):
        content = "| Plant: {0} | Start Weight: {1} | End Weight: {2} | Status: {3} |\n".format(
            self.plant_id, self.start_weight, self.end_weight, self.status)

        top_bottom = ''
        for _ in content:
            top_bottom += '_'
        top_bottom += '\n'

        top_bottom = ''
        for _ in content:
            top_bottom += '_'
        top_bottom += '\n'

        return top_bottom + content + top_bottom

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
        try:
            self.start_weight = int(start_weight)
        except ValueError:
            self.start_weight = 'NULL'

    def get_start_weight(self):
        """Gets the start weight of a plant"""
        return self.start_weight

    def set_end_weight(self, end_weight):
        """Sets the end weight of a plant after watering"""
        try:
            self.end_weight = int(end_weight)
        except ValueError:
            self.start_weight = 'NULL'

    def get_end_weight(self):
        """Gets the end weight of a plant after watering"""
        return self.end_weight

    def get_target_weight(self):
        """Gets the target weight of a plant"""
        return self.target_weight - 5  # may need  to remove this at some point

    def get_status(self):
        """Gets the status of watering"""
    
        if self.end_weight < (self.target_weight - 20) or\
                self.end_weight > (self.target_weight + 20):
            self.set_status(1)
        return self.status

    def set_status(self, status):
        """Sets a status indicating how the watering went"""
        self.status = status

    def get_experiment_id(self):
        """Gets the experiment id"""
        return self.experiment_id

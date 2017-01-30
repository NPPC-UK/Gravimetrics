"""Classes with data on plants"""


class Plant(object):

    # pylint: disable-msg=too-many-instance-attributes
    # pylint: disable-msg=too-many-arguments
    """
    Class to act as a container for plant data
    This is a very altered version of what gravimetrics 
    already uses to contain plants... maybe they'll merge one day"""

    def __init__(self):
        self.balance_history = {}
        self.watering_history = []

    def add_entry(self, start_weight, time, end_weight=None):
        if end_weight is not None:
            self.watering_history.append(
                {'startweight': start_weight, 'endweight': end_weight, 'date': time})
        else:
            self.balance_history[time] = start_weight

    def get_balance_history(self):
        return self.balance_history

    def get_watering_history(self):
        return self.watering_history

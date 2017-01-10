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

    def add_entry(self, weight, time):
        self.balance_history[time] = weight

    def get_balance_history(self):
        return self.balance_history

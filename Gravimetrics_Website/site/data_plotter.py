import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#from datetime import datetime
import mpld3


def generateFakeGraph(plantId):

    plantId = plantId.replace('plant_', '')
    data = [1, int(plantId), 3, 4]
    plt.plot(data)
    fig, ax = plt.subplots()
    ax.plot(data)
    return mpld3.fig_to_html(fig)


def generateBalanceHistory(connection, plantId, numDays=1):
    plantId = plantId.replace('plant_', '')

    plant = connection.get_balance_history(plantId, numDays)

    data = plant.get_balance_history()
    y = []

    for k, v in data.items():
        print(v)
        y.append(v)

    y = y[0::20]  # sample every 20 minutes to make easier to read graph

    plt.plot(y)
    plt.grid(True)

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(y)
    return mpld3.fig_to_html(fig)

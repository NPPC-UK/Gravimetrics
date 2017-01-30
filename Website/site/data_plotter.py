from random import randint
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3
#from datetime import datetime


def generateFakeGraph(plantId):

    plantId = plantId.replace('plant_', '')
    data = [1, int(plantId), 3, 4]
    plt.plot(data)
    fig, ax = plt.subplots()
    ax.plot(data)
    return mpld3.fig_to_html(fig)


def generateWaterHistory(connection, plantId, numDays=7):
    plantId = plantId.replace('plant_', '')

    # TODO generate DATA FROM REAL SOURCES!!!

    plants = connection.get_watering_history(plantId, numDays)
    #atering_readings = []

    #########################################################
    # # Create data                                         #
    # watering_readings = []                                #
    # for plant in range(30):                               #
    #     # for example for 30 days of watering             #
    #                                                       #
    #     date = plant  # just use dates as X inc for now   #
    #                                                       #
    #     # Give some deviation for these guys so that they #
    #     # look a bit more interesting                     #
    #     start = randint(1300, 1400)                       #
    #     end = randint(1499, 1505)                         #
    #                                                       #
    #     watering_run = {'startweight': start,             #
    #                     'endweight': end,                 #
    #                     'date': date}                     #
    #                                                       #
    #     watering_readings.append(watering_run)            #
    #########################################################

    
    # combine these different collections into a list
    bar1 = []
    bar2 = []

    for x in plants.get_watering_history():
        bar1.append(x['startweight'])
        bar2.append(x['endweight'])

    #for x in range(len(bar2)):
    #    bar2[x] = bar2[x] - bar1[x]

    #minimum = min(bar1)
    #for x in range(len(bar1)):
    #    bar1[x] = bar1[x] - minimum

    width = 0.8

    c2 = 'b'
    c1 = 'r'

    ind = np.arange(len(bar1))

    fig, ax = plt.subplots(figsize=(20, 10))

    p1 = ax.bar(ind, bar1, width, color=c1)
    p2 = ax.bar(ind, bar2, width, color=c2, bottom=bar1)

    ax.set_ylim(ymin=min(bar1))
    ax.set_xticks(ind + width / 2., range(len(bar1)))
    #ax.set_yticks(np.arange(0, (max(bar1) + max(bar2)), 20))

    ax.grid()
    ax.legend((p1[0], p2[0]), ('Start Weight', 'Water Added'))

    return mpld3.fig_to_html(fig)


def generateBalanceHistory(connection, plantId, numDays=1):
    plantId = plantId.replace('plant_', '')

    plant = connection.get_balance_history(plantId, numDays)

    data = plant.get_balance_history()
    y = []

    for k, v in data.items():
        if v == 0:
            y.append(y[-1])
            continue
        y.append(v)

    y = y[0::20]  # sample every 20 minutes to make easier to read graph

    print(y)

    plt.plot(y)
    plt.grid(True)

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(y)  # not sure what this does really...
    ax.grid(True)
    # fig.ylabel('Weight')
    # fig.title('Minutes')
    ax.set_title('ax1 title')

    return mpld3.fig_to_html(fig)

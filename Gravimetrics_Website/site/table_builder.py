"""
This is used to generate the tables for the gravi display page
"""
from web import form
from database import Connection
# pylint: disable-msg=invalid-name


def generatePlantWeightForm(listOfTextBoxes):
    """
    This generates the form used in updating plants
    """
    return form.Form(*(listOfTextBoxes + [form.Button('Update', type='submit',
                                                      id='submit', description='Update')]))


def generateTextBoxes():
    """
    This generates the textboxes
    used in the plants updating form
    """
    tmpList = []
    for idx in range(120):
        tmpList.append(form.Textbox(
            'plant_{0}'.format(idx), form.notnull, form.regexp(
                r'\d+', 'Must be a digit'),
            value='{0}'.format(idx)))
    return tmpList


def getPlants():
    """
    Uses code very similar to the gravi db to grab plants from
    the database
    """
    myconn = Connection()
    with open('dbinfo.txt', 'r') as f:
        passwd = f.readline()

    myconn.create_connection('venom.ibers', 'gravi', passwd, 'test')
    curPlants = {}
    for bench in range(8):
        curPlants[bench] = (myconn.get_plants(bench))
    return curPlants


def getTable():
    myDict = {'headers': ['Plant Name', 'Balance Location', 'Target Weight']}
    benches = []
    plants = []
    # this is for testing so generating some plants
    for idx in range(len(plantsTextBoxList)):
        p = {'name': 'plant_{0}'.format(idx),
             'balance': 'balance_{0}'.format(idx),
             'weight': plantsTextBoxList[idx].render}
        plants.append(p)

    for idx in range(0, len(plants), 16):
        benches.append(plants[idx: idx + 16])

    #myDict['plants'] = plants
    myDict['benches'] = benches
    return myDict


# We need to have some kind of global access to this *for now*
# This list contains pointers to the objects of the textboxes for the
# update form
plantsTextBoxList = generateTextBoxes()
plantsForm = generatePlantWeightForm(plantsTextBoxList)

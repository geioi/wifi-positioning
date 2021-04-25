import settings
from iw_scanner import scanAndParse
from gather_data import getInterface
from gui_helper import printToConsole
import mysql.connector


def getMaxValueKey(dictionary):
    values = list(dictionary.values())
    keys = list(dictionary.keys())
    return keys[values.index(max(values))]

def findLocation(interface, with_adapter, sudo_pw=None, gui=False):
    cursor = cnx.cursor(buffered=True)

    table_place = 'place'
    table_place_detail = 'place_detail'
    if not with_adapter:
        table_place += '_without_adapter'
        table_place_detail += '_without_adapter'

    query = 'SELECT p.location ' \
            'FROM access_point ap ' \
            'INNER JOIN ' + table_place + ' p ON ap.id=p.access_point_id ' \
            'WHERE ap.bssid = %(bssid)s ' \
            'AND %(signal_str)s BETWEEN p.signal_str_min AND p.signal_str_max'

    possible_locations = {}
    percentages = {}

    scanResults = scanAndParse(interface, sudo_pw)

    if not scanResults:
        if gui:
            printToConsole('No results found with given interface')
        else:
            print('No results found with given interface')
        return

    for result in scanResults:
        cursor.execute(query, {'bssid': result['mac'], 'signal_str': result['signal_level_dBm']})
        locations = cursor.fetchall()
        if gui:
            printToConsole("locations for mac %s with ssid %s and signal strength %s\n" % (result['mac'], result['essid'], result['signal_level_dBm']))
            printToConsole(str(locations) + '\n')
        else:
            print("locations for mac %s with ssid %s and signal strength %s" % (result['mac'], result['essid'], result['signal_level_dBm']))
            print(locations)
        for item in locations:
            location = item[0]
            if location in possible_locations:
                possible_locations[location] += 1
            else:
                possible_locations[location] = 1

    if gui:
        printToConsole('Locations counts - ' + str(possible_locations) + '\n')
    else:
        print(possible_locations)

    #calculate percentages
    for key, value in possible_locations.items():
        percentages[key] = str(round(value / len(scanResults) * 100, 2)) + '%'

    if gui:
        printToConsole('Likelihood percentages - ' + str(percentages) + '\n')
    else:
        print(percentages)
    if possible_locations:
        if gui:
            printToConsole('Your current location is most probably ' + str(getMaxValueKey(possible_locations)) + '\n')
        else:
            print('Your current location is most probably ' + str(getMaxValueKey(possible_locations)))
    else:
        if gui:
            printToConsole('No matching results found. Unable to locate you. Try to scan again or change to another database table\n')
        else:
            print('No matching results found. Unable to locate you. Try to scan again or change to another database table')

def usesExternalAdapter():
    answer = input('Interface is an external adapter (yes/no): ')
    if answer not in ['yes', 'no', 'y', 'n']:
        exit()
    return answer

def locateWithoutGui(interface, with_adapter):
    global cnx, use_database
    db_config = {
        'user': settings.USERNAME,
        'password': settings.PASSWORD,
        'host': settings.HOST,
        'database': settings.DATABASE,
        'raise_on_warnings': True
    }
    try:
        cnx = mysql.connector.connect(**db_config)
    except:
        print('[!] Could not connect to the database')
        print('Terminating...')
        exit()

    findLocation(interface, with_adapter, settings.SUDO_PW)

    if cnx:
        cnx.close()

def locateWithGui(database_connection, interface, with_adapter, sudo_pw):
    global cnx
    cnx = database_connection
    findLocation(interface, with_adapter, sudo_pw, gui=True)

if __name__ == "__main__":
    yes_no_dict = {'yes': True, 'y': True, 'no': False, 'n': False}
    interface = getInterface()
    uses_external_adapter = yes_no_dict[usesExternalAdapter()]
    locateWithoutGui(interface, uses_external_adapter)

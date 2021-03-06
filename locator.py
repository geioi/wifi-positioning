import settings
from iw_scanner import scanAndParse
from gather_data import getInterface
import mysql.connector

def findLocation(interface, with_adapter, sudo_pw=None):
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

    scanResults = scanAndParse(interface, sudo_pw)

    if not scanResults:
        print('No results found with given interface')
        return

    for result in scanResults:
        cursor.execute(query, {'bssid': result['mac'], 'signal_str': result['signal_level_dBm']})
        locations = cursor.fetchall()
        print("locations for mac %s with ssid %s and signal strength %s" % (result['mac'], result['essid'], result['signal_level_dBm']))
        print(locations)
        for item in locations:
            location = item[0]
            if location in possible_locations:
                possible_locations[location] += 1
            else:
                possible_locations[location] = 1

    print(possible_locations)
        #print(result)

def usesExternalAdapter():
    answer = input('Interface is used by an external adapter? (yes/no): ')
    if answer not in ['yes', 'no']:
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
    findLocation(interface, with_adapter, sudo_pw)

if __name__ == "__main__":
    yes_no_dict = {'yes': True, 'no': False}
    interface = getInterface()
    uses_external_adapter = yes_no_dict[usesExternalAdapter()]
    locateWithoutGui(interface, uses_external_adapter)
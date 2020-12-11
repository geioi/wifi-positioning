#!/usr/bin/env python3
import os
import subprocess

import pyshark
import mysql.connector
from pyshark.tshark.tshark import get_process_path
import settings
#import sys


def get_tshark_interface_names(tshark_path=None):
    parameters = [get_process_path(tshark_path), "-D"]
    with open(os.devnull, "w") as null:
        tshark_interfaces = subprocess.check_output(parameters, stderr=null).decode("utf-8")

    return [line.split(". ")[1] for line in tshark_interfaces.splitlines()]

def analyzeData(capture):
    print('-------------------Processing data-------------------')

    ssid_dict = {}
    signal_str_min_dict = {}
    signal_str_max_dict = {}
    signal_str = None
    bssid = None
    ssid = None

    for packet in capture:
        for layer in packet.layers:
            if layer.get('signal_dbm'):
                signal_str = int(layer.get('signal_dbm'))
            elif layer.get('bssid'):
                bssid = layer.get('bssid')
            elif layer.get('ssid'):
                ssid = layer.get('ssid')

        if not bssid in ssid_dict:
            ssid_dict[bssid] = ssid

        if bssid in signal_str_min_dict:
            if signal_str < signal_str_min_dict[bssid]:
                signal_str_min_dict[bssid] = signal_str
        else:
            signal_str_min_dict[bssid] = signal_str

        if bssid in signal_str_max_dict:
            if signal_str > signal_str_max_dict[bssid]:
                signal_str_max_dict[bssid] = signal_str
        else:
            signal_str_max_dict[bssid] = signal_str

        signal_str = None
        bssid = None
        ssid = None
    print('-------------------Done processing new data-------------------')
    return ssid_dict, signal_str_min_dict, signal_str_max_dict


def addDataToDb(building, location, specified_location, floor, ssid_dict, signals_min_dict, signals_max_dict):
    global cnx
    print('-------------------Adding data to DB-------------------')

    add_access_point = ("INSERT INTO access_point "
                    "(bssid, ssid) "
                    "VALUES (%s, %s)")

    add_place = ("INSERT INTO place "
                        "(building, location, floor, access_point_id, signal_str_min, signal_str_max) "
                        "VALUES (%s, %s, %s, %s, %s, %s)")

    add_place_detail = ("INSERT INTO place_detail "
                 "(place_id, detailed_location, access_point_id, signal_str_min, signal_str_max) "
                 "VALUES (%s, %s, %s, %s, %s)")

    cursor = cnx.cursor(buffered=True)

    for item in ssid_dict.items():
        cursor.execute('SELECT id '
                 'FROM access_point '
                 'WHERE bssid=' + '"' + item[0] + '"')
        ap_id = cursor.fetchone()

        if ap_id:
            cursor.execute('SELECT id, signal_str_min, signal_str_max '
                           'FROM place '
                           'WHERE location=' + '"' + location + '" '
                           'AND floor=' + str(floor) + ' '
                           'AND access_point_id=' + str(ap_id[0]) + ' '
                           'AND building="' + building + '"')
            place_data = cursor.fetchone()
            if place_data:
                place_id = place_data[0]
            else:
                place_id = False
            if place_id:
                data_place_detail = (place_id, specified_location, ap_id[0], signals_min_dict[item[0]], signals_max_dict[item[0]])
                if signals_min_dict[item[0]] < place_data[1]:
                    cursor.execute('UPDATE place '
                                   'SET signal_str_min=' + str(signals_min_dict[item[0]]) + ' '
                                   'WHERE id=' + str(place_id))
                if signals_max_dict[item[0]] > place_data[2]:
                    cursor.execute('UPDATE place '
                                   'SET signal_str_max=' + str(signals_max_dict[item[0]]) + ' '
                                   'WHERE id=' + str(place_id))
            else:
                data_place = (building, location, floor, ap_id[0], signals_min_dict[item[0]], signals_max_dict[item[0]])
                cursor.execute(add_place, data_place)
                data_place_detail = (cursor.lastrowid, specified_location, ap_id[0], signals_min_dict[item[0]], signals_max_dict[item[0]])

        else:
            data_ap = (item[0], item[1])
            cursor.execute(add_access_point, data_ap)
            ap_id = cursor.lastrowid
            data_place = (building, location, floor, ap_id, signals_min_dict[item[0]], signals_max_dict[item[0]])
            cursor.execute(add_place, data_place)
            data_place_detail = (cursor.lastrowid, specified_location, ap_id, signals_min_dict[item[0]], signals_max_dict[item[0]])

        cursor.execute(add_place_detail, data_place_detail)

    cnx.commit()
    cursor.close()
    print('-------------------Done adding items to database-------------------')

def captureFromFile(building, location, specified_location, floor, input_file):
    global use_database
    cap = pyshark.FileCapture(input_file, debug=False)
    ssids, signals_min, signals_max = analyzeData(cap)
    cap.close()
    if use_database:
        addDataToDb(building, location, specified_location, floor, ssids, signals_min, signals_max)

def captureDataLive(interface, building, location, specified_location, floor, filename, packetCount=500):
    capture_file = 'pcap_dumps/' + filename + '_' + specified_location.replace(' ', '_') + '.pcap'
    #add check if interface is in monitor mode or set timeout
    capture = pyshark.LiveCapture(interface=interface, output_file=capture_file, debug=False, bpf_filter='wlan type mgt subtype beacon')
    print('-------------------Starting data capture-------------------')
    capture.load_packets(packetCount)
    print('-------------------Data captured-------------------')
    ssids, signals_min, signals_max = analyzeData(capture)
    if use_database:
        addDataToDb(building, location, specified_location, floor, ssids, signals_min, signals_max)



def initMethod(building, room, floor, roomSize=None, specific_location=None, method=None, fileName=None, packet_count=500, interface=None):
    if method == 'live':
        if specific_location:
            print('[+] Mapping custom area in the room')
            customAreaMethod(building, room, floor, specific_location, packet_count, interface)
        elif roomSize:
            if roomSize == 'S':
                print('[+] Using centering method to map the room')
                centerMethod(building, room, floor, packet_count, interface)
            elif roomSize == 'M':
                locations = ['upper right', 'upper left', 'lower left', 'lower right']
                print('[+] Using left-right method to map the room')
                for location in locations:
                    leftRightMethod(building, room, floor, packet_count, interface, location)
            else:
                locations = ['north-east', 'north-west', 'south-west', 'south-east']
                print('[+] Using NESW method to map the room')
                for location in locations:
                    NESWMethod(building, room, floor, packet_count, interface, location)
        else:
            locations = ['north-east', 'north-west', 'south-west', 'south-east']
            print('[+] Using NESW method by default to map the room')
            for location in locations:
                NESWMethod(building, room, floor, packet_count, interface, location)
    else:
        captureFromFile(building, room, specific_location, floor, fileName)
        while True:
            print('[+] Enter another file name for processing (or press enter to finish)')
            fileName = getFileName()
            specific_location = input('[+] Enter new specific location name for this file (or press enter to finish): ')
            if specific_location == '':
                return

            captureFromFile(building, room, specific_location, floor, fileName)


### capturing methods
def leftRightMethod(building, location, floor, packetCount=500, interface=None, side=None):
    command = input('[!] Please move to the ' + side + ' side of the room and press Enter (or type anything and press Enter to exit): ')
    if command == '':
        captureDataLive(interface, building, location, side + ' side', floor, side + '_side', packetCount)
    else:
        print('Exiting...')
        exit()


def NESWMethod(building, location, floor, packetCount=500, interface=None, corner=None):
    command = input('[!] Please move to the ' + corner + ' corner of the room and press Enter (or type anything and press Enter to exit): ')
    if command == '':
        captureDataLive(interface, building, location, corner + ' corner', floor, corner + '_corner', packetCount)
    else:
        print('Exiting...')
        exit()

def centerMethod(building, location, floor, packetCount=500, interface=None):
    command = input('[!] Please move to the center of the room and press Enter (or type anything and press Enter to exit): ')
    if command == '':
        captureDataLive(interface, building, location, 'center', floor, 'center', packetCount)
    else:
        print('Exiting...')
        exit()

def customAreaMethod(building, location, floor, specific_location, packetCount=500, interface=None):
    command = input('[!] Please move to the specified place (' + specific_location + ') in the room and press Enter (or type anything and press Enter to exit): ')
    if command == '':
        captureDataLive(interface, building, location, specific_location, floor, specific_location.replace(' ', '_'), packetCount)
    else:
        print('Exiting...')
        exit()


### input functions
def getMethod():
    method = input('[?] Please enter the name of the method (file|live): ')
    if method == '':
        exit()
    if method == 'file' or method == 'live':
        return method
    print('Invalid input!')
    return getMethod()

def getInterface(available_interfaces=None):
    if available_interfaces == None:
        available_interfaces = get_tshark_interface_names(get_process_path())
    interface = input('[?] Please enter the name of the interface: ')
    if interface == '':
        exit()

    if interface in available_interfaces:
        return interface
    print('Given interface does not seem to exist! Available interfaces are ' + str(available_interfaces))
    return getInterface(available_interfaces)

def getFileName(accepted_extensions=None):
    if accepted_extensions is None:
        accepted_extensions = ['pcap', 'pcapng']
    fileName = input('[?] Please enter the name of the file (ending in .pcap or .pcapng): ')
    if fileName == '':
        exit()
    if fileName.split('.')[-1] in accepted_extensions:
        if os.path.exists(fileName):
            return fileName
        print('Specified file could not be found!')
        return getFileName()
    print('Input file can only be with extension .pcap and .pcapng')
    return getFileName()

def getBuilding():
    building = input('[?] Please enter the name of the building: ')
    if building == '':
        exit()
    return building.lower()

def getFloor():
    floor = input('[?] Building floor: ')
    if floor == '':
        exit()
    if floor.isdigit():
        return int(floor)
    print('Floor can only be in a form of digit')
    return getFloor()

def getRoom(building=None, possible_locations=None, confirm=False, last_choice=None):
    global cnx
    room = input('[?] Room name: ')
    if room == '' and not confirm:
        exit()
    elif room == '' and confirm:
        return last_choice
    elif room != '' and confirm and room in possible_locations:
        return room

    cursor = cnx.cursor(buffered=True)
    cursor.execute('SELECT DISTINCT location '
                   'FROM place '
                   'WHERE building=' + '"' + building + '" '
                   'AND levenshtein("' + room + '", location) < 3')
                   #'AND location LIKE "%' + room + '%"')
    locations = cursor.fetchall()
    #print(locations)
    locations = [location[0] for location in locations]
    #print(locations)

    if room in locations:
        print('[+] Room found in database already, no new entry will be added but SSIDs and signal strengths will be updated.')
    elif locations:
        print('Rooms with similar names found: ' + str(locations))
        print('Press enter again to confirm your current choice. Or enter the name from the given options you would like to use.')
        return getRoom(building, possible_locations=locations, confirm=True, last_choice=room)
    return room

def getRoomSize(allowed_sizes=None):
    if allowed_sizes is None:
        allowed_sizes = ['S', 'M', 'L']
    size = input('[+] (Optional) Enter room size (S, M, L): ')
    if size == '':
        return None
    size = size.upper()
    if size in allowed_sizes:
        return size
    print('Invalid input! only S, M, L is allowed as input for this field')
    return getRoomSize()

def getSpecificLocation(method):
    if method == 'live':
        specific_location = input('[+] (Optional) Enter more specific location in the room (by the window etc.): ')
        if specific_location == '':
            return None
    else:
        specific_location = input('[+] (Required) Enter more specific location in the room (by the window etc.): ')
        if specific_location == '':
            exit()
    return specific_location

def getPacketCount():
    packet_count = input('[+] (Optional) Enter the packet amount before terminating (default is 500): ')
    if packet_count == '':
        return 500
    if packet_count.isdigit():
        return int(packet_count)
    print('Invalid input! Packet count has to be a digit')
    return getPacketCount()

def askForInput():
    method = getMethod()
    building = getBuilding()
    floor = getFloor()
    room = getRoom(building)
    specific_location = getSpecificLocation(method)
    if not specific_location:
        roomSize = getRoomSize()
    else:
        roomSize = None

    interface = None
    packet_count = None
    fileName = None

    if method == 'live':
        interface = getInterface()
        packet_count = getPacketCount()
    else:
        fileName = getFileName()

    return method, building, floor, room, roomSize, specific_location, interface, packet_count, fileName


use_database = True
cnx = None

def main():
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
        answer = input('Could not establish connection to database or table name is not correct. Continue anyway? (yes/no): ')
        if answer != 'yes':
            exit()
        use_database = False

    method, building, floor, room, roomSize, specific_location, interface, packet_count, fileName = askForInput()

    initMethod(building, room, floor, roomSize, specific_location, method, fileName, packet_count, interface)

    print('[+] Scan complete room ' + room + ' now mapped!')
    if cnx:
        cnx.close()

if __name__ == "__main__":
    main()




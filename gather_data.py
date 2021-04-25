#!/usr/bin/env python3
import os
import subprocess

import pyshark
import mysql.connector
from pyshark.tshark.tshark import get_process_path
import settings
import iw_scanner
from gui_helper import printToConsole, askConfirmation
#import sys


def get_tshark_interface_names(tshark_path=None):
    parameters = [get_process_path(tshark_path), "-D"]
    with open(os.devnull, "w") as null:
        tshark_interfaces = subprocess.check_output(parameters, stderr=null).decode("utf-8")

    return [line.split(". ")[1] for line in tshark_interfaces.splitlines()]

def analyzeData(capture, gui=False):
    if gui:
        print('-------------------Processing data-------------------')
        printToConsole('-------------------Processing data-------------------\n')
    else:
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
            elif layer.get('wlan.ssid'):
                ssid = layer.get('wlan.ssid')

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
    if gui:
        print('-------------------Done processing new data-------------------')
        printToConsole('-------------------Done processing new data-------------------\n')
    else:
        print('-------------------Done processing new data-------------------')
    return ssid_dict, signal_str_min_dict, signal_str_max_dict


def addDataToDb(building, location, specified_location, floor, ssid_dict, signals_min_dict, signals_max_dict, without_adapter=False, gui=False):
    global cnx
    if gui:
        print('-------------------Adding data to DB-------------------')
        printToConsole('-------------------Adding data to DB-------------------\n')
    else:
        print('-------------------Adding data to DB-------------------')

    table_place = 'place'
    table_place_detail = 'place_detail'

    if without_adapter:
        table_place += '_without_adapter'
        table_place_detail += '_without_adapter'

    add_access_point = ("INSERT INTO access_point "
                    "(bssid, ssid) "
                    "VALUES (%s, %s)")

    add_place = ("INSERT INTO " + table_place + " "
                        "(building, location, floor, access_point_id, signal_str_min, signal_str_max) "
                        "VALUES (%s, %s, %s, %s, %s, %s)")

    add_place_detail = ("INSERT INTO " + table_place_detail + " "
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
                           'FROM ' + table_place + ' '
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
                    cursor.execute('UPDATE ' + table_place + ' '
                                   'SET signal_str_min=' + str(signals_min_dict[item[0]]) + ' '
                                   'WHERE id=' + str(place_id))
                if signals_max_dict[item[0]] > place_data[2]:
                    cursor.execute('UPDATE ' + table_place + ' '
                                   'SET signal_str_max=' + str(signals_max_dict[item[0]]) + ' '
                                   'WHERE id=' + str(place_id))
            else:
                data_place = (building, location, floor, ap_id[0], signals_min_dict[item[0]], signals_max_dict[item[0]])
                cursor.execute(add_place, data_place)
                data_place_detail = (cursor.lastrowid, specified_location, ap_id[0], signals_min_dict[item[0]], signals_max_dict[item[0]])

        else:
            if item[1] == None:
                item = list(item) #convert to list as tuples are immutable
                item[1] = 'Unknown'
            data_ap = (item[0], item[1])
            cursor.execute(add_access_point, data_ap)
            ap_id = cursor.lastrowid
            data_place = (building, location, floor, ap_id, signals_min_dict[item[0]], signals_max_dict[item[0]])
            cursor.execute(add_place, data_place)
            data_place_detail = (cursor.lastrowid, specified_location, ap_id, signals_min_dict[item[0]], signals_max_dict[item[0]])

        cursor.execute(add_place_detail, data_place_detail)

    cnx.commit()
    cursor.close()
    if gui:
        print('-------------------Done adding items to database-------------------')
        printToConsole('-------------------Done adding items to database-------------------\n')
    else:
        print('-------------------Done adding items to database-------------------')

def captureFromFile(building, location, specified_location, floor, input_file, gui=False):
    global use_database
    cap = pyshark.FileCapture(input_file, debug=False)
    ssids, signals_min, signals_max = analyzeData(cap, gui)
    cap.close()
    if use_database:
        addDataToDb(building, location, specified_location, floor, ssids, signals_min, signals_max, gui=gui)

def captureDataLive(interface, building, location, specified_location, floor, filename, packetCount=500, sudo_pw=None, gui=False, internal_adapter_only=False, internal_interface = None):
    capture_file = 'pcap_dumps/' + filename + '_' + specified_location.replace(' ', '_') + '.pcap'
    if not internal_adapter_only:
        #add check if interface is in monitor mode or set timeout
        capture = pyshark.LiveCapture(interface=interface, output_file=capture_file, debug=False, bpf_filter='wlan type mgt subtype beacon')
        if gui:
            print('-------------------Starting data capture with adapter-------------------')
            printToConsole('-------------------Starting data capture with adapter-------------------\n')
        else:
            print('-------------------Starting data capture with adapter-------------------')
        capture.load_packets(packetCount)
        if gui:
            print('-------------------Data captured-------------------')
            printToConsole('-------------------Data captured-------------------\n')
        else:
            print('-------------------Data captured-------------------')
        ssids, signals_min, signals_max = analyzeData(capture, gui)
        if use_database:
            addDataToDb(building, location, specified_location, floor, ssids, signals_min, signals_max, gui=gui)
    if gui:
        print('-------------------Executing scans without adapter-------------------')
        printToConsole('-------------------Executing scans without adapter-------------------\n')
    else:
        print('-------------------Executing scans without adapter-------------------')
    ssids_without_adapter, signals_min_without_adapter, signals_max_without_adapter = iw_scanner.doMultipleScans(internal_interface, sudo_pw)
    if gui:
        print('-------------------Done executing scans without adapter-------------------')
        printToConsole('-------------------Done executing scans without adapter-------------------\n')
    else:
        print('-------------------Done executing scans without adapter-------------------')
    if use_database:
        addDataToDb(building, location, specified_location, floor, ssids_without_adapter, signals_min_without_adapter, signals_max_without_adapter, without_adapter=True, gui=gui)


def initMethod(building, room, floor, roomSize=None, specific_location=None, method=None, fileName=None, packet_count=500, interface=None, gui=False, sudo_pw=None, internal_adapter_only=False, internal_interface=None):
    if method == 'live':
        if specific_location:
            if gui:
                printToConsole('[+] Mapping custom area in the room\n')
            else:
                print('[+] Mapping custom area in the room')
            abort_command = customAreaMethod(building, room, floor, specific_location, packet_count, interface, gui, sudo_pw, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
            if abort_command:
                return abort_command
        elif roomSize:
            if roomSize == 'S':
                if gui:
                    printToConsole('[+] Using centering method to map the room\n')
                else:
                    print('[+] Using centering method to map the room')
                abort_command = centerMethod(building, room, floor, packet_count, interface, gui, sudo_pw, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
                if abort_command:
                    return abort_command
            elif roomSize == 'M':
                locations = ['left', 'right']
                if gui:
                    printToConsole('[+] Using left-right method to map the room\n')
                else:
                    print('[+] Using left-right method to map the room')
                for location in locations:
                    abort_command = leftRightMethod(building, room, floor, packet_count, interface, location, gui, sudo_pw, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
                    if abort_command:
                        return abort_command
            else:
                locations = ['north-east', 'north-west', 'south-west', 'south-east']
                if gui:
                    printToConsole('[+] Using NESW method to map the room\n')
                else:
                    print('[+] Using NESW method to map the room')
                for location in locations:
                    abort_command = NESWMethod(building, room, floor, packet_count, interface, location, gui, sudo_pw, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
                    if abort_command:
                        return abort_command
        else:
            locations = ['north-east', 'north-west', 'south-west', 'south-east']
            if gui:
                printToConsole('[+] Using NESW method by default to map the room\n')
            else:
                print('[+] Using NESW method by default to map the room')
            for location in locations:
                abort_command = NESWMethod(building, room, floor, packet_count, interface, location, gui, sudo_pw, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
                if abort_command:
                    return abort_command
    else:
        captureFromFile(building, room, specific_location, floor, fileName, gui)

        if not gui:
            while True:
                print('[+] Enter another file name for processing (or press enter to finish)')
                fileName = getFileName()
                specific_location = input('[+] Enter new specific location name for this file (or press enter to finish): ')
                if specific_location == '':
                    return

                captureFromFile(building, room, specific_location, floor, fileName)


### capturing methods
def leftRightMethod(building, location, floor, packetCount=500, interface=None, side=None, gui=False, sudo_pw=None, internal_adapter_only=False, internal_interface=None):
    if gui:
        printToConsole('[!] Please move to the ' + side + ' side of the room and press Continue (or Abort to exit): \n')
        command = askConfirmation(gui)
    else:
        command = input('[!] Please move to the ' + side + ' side of the room and press Enter (or type anything and press Enter to exit): ')
    if command == '':
        captureDataLive(interface, building, location, side + ' side', floor, location, packetCount, sudo_pw, gui, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
    else:
        if gui:
            printToConsole('Aborting..\n')
            return 'Abort'
        print('Exiting...')
        exit()


def NESWMethod(building, location, floor, packetCount=500, interface=None, corner=None, gui=False, sudo_pw=None, internal_adapter_only=False, internal_interface=None):
    if gui:
        printToConsole('[!] Please move to the ' + corner + ' corner of the room and press Continue (or Abort to exit): \n')
        command = askConfirmation(gui)
    else:
        command = input('[!] Please move to the ' + corner + ' corner of the room and press Enter (or type anything and press Enter to exit): ')
    if command == '':
        captureDataLive(interface, building, location, corner + ' corner', floor, location, packetCount, sudo_pw, gui, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
    else:
        if gui:
            printToConsole('Aborting..\n')
            return 'Abort'
        print('Exiting...')
        exit()

def centerMethod(building, location, floor, packetCount=500, interface=None, gui=False, sudo_pw=None, internal_adapter_only=False, internal_interface=None):
    if gui:
        printToConsole('[!] Please move to the center of the room and press Continue (or Abort to exit): \n')
        command = askConfirmation(gui)
    else:
        command = input('[!] Please move to the center of the room and press Enter (or type anything and press Enter to exit): ')
    if command == '':
        captureDataLive(interface, building, location, 'center', floor, location, packetCount, sudo_pw, gui, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
    else:
        if gui:
            printToConsole('Aborting..\n')
            return 'Abort'
        print('Exiting...')
        exit()

def customAreaMethod(building, location, floor, specific_location, packetCount=500, interface=None, gui=False, sudo_pw=None, internal_adapter_only=False, internal_interface=None):
    if gui:
        printToConsole('[!] Please move to the specified place (' + specific_location + ') in the room and press Continue (or Abort to exit): \n')
        command = askConfirmation(gui)
    else:
        command = input('[!] Please move to the specified place (' + specific_location + ') in the room and press Enter (or type anything and press Enter to exit): ')
    if command == '':
        captureDataLive(interface, building, location, specific_location, floor, location.replace(' ', '_'), packetCount, sudo_pw, gui, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
    else:
        if gui:
            printToConsole('Aborting..\n')
            return 'Abort'
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
    interface = input('[?] Please enter the name of the adapter interface: ')
    if interface == '':
        exit()

    if interface in available_interfaces:
        return interface
    print('Given interface does not seem to exist! Available interfaces are ' + str(available_interfaces))
    return getInterface(available_interfaces)

def isExternalInterface():
    answer = input('Interface is an external adapter (yes/no): ')
    if answer not in ['yes', 'no', 'y', 'n']:
        exit()
    return answer

def getInternalInterface(available_interfaces=None):
    if available_interfaces == None:
        available_interfaces = get_tshark_interface_names(get_process_path())
    interface = input('[?] Please enter the name of the internal built-in network interface: ')
    if interface == '':
        exit()

    if interface in available_interfaces:
        return interface
    print('Given interface does not seem to exist! Available interfaces are ' + str(available_interfaces))
    return getInternalInterface(available_interfaces)

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
    if cnx:
        cursor = cnx.cursor(buffered=True)
        cursor.execute('SELECT DISTINCT location '
                       'FROM place '
                       'WHERE building=' + '"' + building + '" '
                       'AND levenshtein("' + room + '", location) < 3')
        locations = cursor.fetchall()
        locations = [location[0] for location in locations]

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

def askForInput():
    yes_no_dict = {'yes': True, 'y': True, 'no': False, 'n': False}
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
    is_external_interface = None
    internal_adapter = None
    fileName = None

    if method == 'live':
        interface = getInterface()
        is_external_interface = yes_no_dict[isExternalInterface()]
        if is_external_interface:
            internal_adapter = getInternalInterface()
        else:
            internal_adapter = interface
    else:
        fileName = getFileName()

    return method, building, floor, room, roomSize, specific_location, interface, fileName, internal_adapter, not is_external_interface


use_database = True
cnx = None

def collectWithoutGui():
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
        if answer not in ['yes', 'y']:
            exit()
        use_database = False

    method, building, floor, room, roomSize, specific_location, interface, fileName, internal_adapter, internal_adapter_only = askForInput()
    packet_count = None
    if not internal_adapter_only:
        packet_count = iw_scanner.determinePacketCount(internal_adapter, settings.SUDO_PW)
    initMethod(building, room, floor, roomSize, specific_location, method, fileName, packet_count, interface, False, settings.SUDO_PW, internal_adapter_only=internal_adapter_only, internal_interface=internal_adapter)

    print('[+] Scan complete room ' + room + ' now mapped!')
    if cnx:
        cnx.close()

def collectWithGui(database_connection, building, room, floor, roomSize, specific_location, method, fileName, interface, sudo_pw, gui, internal_interface, internal_adapter_only=False):
    global cnx, use_database
    if database_connection:
        cnx = database_connection
        use_database = True
    else:
        use_database = False
    packet_count = iw_scanner.determinePacketCount(internal_interface, sudo_pw)
    abort_command = initMethod(building, room, floor, roomSize, specific_location, method, fileName, packet_count, interface, gui, sudo_pw, internal_adapter_only=internal_adapter_only, internal_interface=internal_interface)
    if abort_command:
        return
    printToConsole('[+] Scan complete room ' + room + ' now mapped!\n')

if __name__ == "__main__":
    collectWithoutGui()




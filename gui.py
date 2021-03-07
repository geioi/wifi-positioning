import tkinter as tk
import mysql.connector
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askopenfilename

from gather_data import get_tshark_interface_names, get_process_path, collectWithGui
from locator import locateWithGui
from gui_helper import printToConsole, createConsoleArea, clearConsoleArea, createButtonsFrame, askConfirmation
import settings

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

def hideAndShowMethodOptions(method_option):
    if method_option == 'Live':
        file_name_label.grid_remove()
        file_name.grid_remove()
        add_file_btn.grid_remove()
        specific_location_label.grid_remove()
        specific_location.grid_remove()
        data_interface_label.grid()
        data_interface_dropdown_menu.grid()
        choose_one_label.grid()
        room_size_radio_btn.grid()
        specific_location_radio_btn.grid()
        data_is_adapter_checkbox.grid()
    else:
        data_interface_label.grid_remove()
        data_interface_dropdown_menu.grid_remove()
        choose_one_label.grid_remove()
        room_size_radio_btn.grid_remove()
        specific_location_radio_btn.grid_remove()
        room_size_label.grid_remove()
        room_size_radio_s.grid_remove()
        room_size_radio_m.grid_remove()
        room_size_radio_l.grid_remove()
        data_is_adapter_checkbox.grid_remove()
        file_name_label.grid()
        file_name.grid()
        add_file_btn.grid()
        specific_location_label.grid()
        specific_location.grid()

def hideAndShowRadioOptions(radio_option):
    if radio_option == 'room_size':
        specific_location_label.grid_remove()
        specific_location.grid_remove()
        room_size_label.grid()
        room_size_radio_s.grid()
        room_size_radio_m.grid()
        room_size_radio_l.grid()
    else:
        room_size_label.grid_remove()
        room_size_radio_s.grid_remove()
        room_size_radio_m.grid_remove()
        room_size_radio_l.grid_remove()
        specific_location_label.grid()
        specific_location.grid()

def getFile():
    filename = askopenfilename()
    if filename:
        file_name.delete(0, END)
        file_name.insert(0, filename)

def modeChanged(*args):
    hideAndShowMethodOptions(method_dropdown_menu.get())

def selectionChanged(*args):
    hideAndShowRadioOptions(selection_radio.get())

def connectToDatabase(user, password, host, database_table):
    global cnx
    db_config = {
        'user': user,
        'password': password,
        'host': host,
        'database': database_table,
        'raise_on_warnings': True
    }
    try:
        cnx = mysql.connector.connect(**db_config)
    except:
        printToConsole('Could not connect to the database or could not find the given table\n')
        return False

    return cnx

def collectData():
    if not building.get():
        printToConsole('Building field can not be empty\n')
        return
    if not floor.get():
        printToConsole('Floor field can not be empty\n')
        return
    else:
        if not is_integer(floor.get()):
            printToConsole('Floor has to be an integer value\n')
            return
    if not room.get():
        printToConsole('Room field can no be empty\n')
        return

    db_conn = connectToDatabase(user.get(), db_pw.get(), host.get(), db_table.get())
    if not db_conn:
        printToConsole('Would you like to continue anyway?\n')
        answer = askConfirmation(window)
        if answer == 'Abort':
            return
    spec_location = None
    room_size_value = None
    if method_dropdown.get() == 'Live':
        method = 'live'
        interface = data_interface_dropdown.get()
        if not interface:
            printToConsole('Interface is not set\n')
            return
        if selection_radio.get():
            if selection_radio.get() == 'room_size':
                if room_size_radio_selection.get():
                    room_size_value = room_size_radio_selection.get()
                else:
                    printToConsole('Room size has to be specified\n')
                    return
            else:
                if specific_location.get():
                    spec_location = specific_location.get()
                else:
                    printToConsole('Location has to be specified!\n')
                    return
        else:
            printToConsole('You have to specify either room size or more specific location\n')
            return
        clearConsoleArea()
        collectWithGui(database_connection=db_conn,
                       building=building.get(),
                       room=room.get(),
                       floor=floor.get(),
                       roomSize=room_size_value,
                       specific_location=spec_location,
                       method=method,
                       fileName=None,
                       interface=interface,
                       sudo_pw=sudo_pw.get(),
                       gui=window)
    else:
        method = 'file'
        spec_location = specific_location.get()
        clearConsoleArea()
        collectWithGui(database_connection=db_conn,
                       building=building.get(),
                       room=room.get(),
                       floor=floor.get(),
                       roomSize=room_size_value,
                       specific_location=spec_location,
                       method=method,
                       fileName=file_name.get(),
                       interface=None,
                       sudo_pw=sudo_pw.get(),
                       gui=window)
    if db_conn:
        db_conn.close()

def startLocating():
    db_conn = connectToDatabase(user.get(), db_pw.get(), host.get(), db_table.get())
    if not db_conn:
        return
    if locating_interface_dropdown.get():
        clearConsoleArea()
        locateWithGui(database_connection=db_conn, interface=locating_interface_dropdown.get(), with_adapter=locating_is_adapter.get(), sudo_pw=sudo_pw.get())
    else:
        printToConsole('interface is not set\n')
    db_conn.close()

available_interfaces = get_tshark_interface_names(get_process_path())

## Main window
window = tk.Tk()
window.title('Wifi scripts')
window.geometry('800x700')

createConsoleArea(window)

window.grid_columnconfigure(0, weight=1)

createButtonsFrame(window)

## Tabs
tabControl = ttk.Notebook(window)

settings_tab = ttk.Frame(tabControl)
tabControl.add(settings_tab, text='Settings')

data_tab = ttk.Frame(tabControl)
tabControl.add(data_tab, text='Gather data')

locating_tab = ttk.Frame(tabControl)
tabControl.add(locating_tab, text='Locate')

tabControl.grid(row=0, columnspan=3, pady=10, padx=10)

## Settings tab
Label(settings_tab, text="Database username").grid(row=0)
Label(settings_tab, text="Database password").grid(row=1)
Label(settings_tab, text="Database host").grid(row=2)
Label(settings_tab, text="Database table").grid(row=3)
Label(settings_tab, text="Sudo password").grid(row=4)

user = Entry(settings_tab)
db_pw = Entry(settings_tab, show='*')
host = Entry(settings_tab)
db_table = Entry(settings_tab)
sudo_pw = Entry(settings_tab, show='*')

user.grid(row=0, column=1)
db_pw.grid(row=1, column=1)
host.grid(row=2, column=1)
db_table.grid(row=3, column=1)
sudo_pw.grid(row=4, column=1)

## Data gathering tab content
method_dropdown = tk.StringVar()
method_dropdown.set('Live')
method_dropdown_menu = ttk.Combobox(data_tab, textvariable=method_dropdown, values=['Live', 'From file'], justify='center', width=20)
method_dropdown_menu.grid(row=0, columnspan=3)

data_interface_label = Label(data_tab, text="Interface name")
data_interface_label.grid(row=1)
building_label = Label(data_tab, text="Building").grid(row=2)
floor_label = Label(data_tab, text="Floor").grid(row=3)
room_label = Label(data_tab, text="Room").grid(row=4)
choose_one_label = Label(data_tab, text="Choose one")
choose_one_label.grid(row=5)

room_size_label = Label(data_tab, text="Room size")
room_size_label.grid(row=6)
specific_location_label = Label(data_tab, text="Specific location")
specific_location_label.grid(row=6)
file_name_label = Label(data_tab, text="File name (ending in .pcap or .pcapng)")
file_name_label.grid(row=1)

method_dropdown.trace(mode='w', callback=modeChanged)

data_interface_dropdown = tk.StringVar()
data_interface_dropdown_menu = ttk.Combobox(data_tab, textvariable=data_interface_dropdown, values=available_interfaces, justify='center',  width=30)
building = Entry(data_tab)
floor = Entry(data_tab)
room = Entry(data_tab)
room_size = Entry(data_tab)
specific_location = Entry(data_tab)
file_name = Entry(data_tab, width=50)

add_file_btn = Button(data_tab, text='Browse..', command=getFile)
add_file_btn.grid(row=1, column=2)

data_interface_dropdown_menu.grid(row=1, column=1)
building.grid(row=2, column=1)
floor.grid(row=3, column=1)
room.grid(row=4, column=1)
room_size.grid(row=6, column=1)
specific_location.grid(row=6, column=1)
file_name.grid(row=1, column=1, padx=10)

selection_radio = tk.StringVar()
room_size_radio_btn = Radiobutton(data_tab, text='Choose a room size', variable=selection_radio, value='room_size')
room_size_radio_btn.grid(row=5, column=1)

specific_location_radio_btn = Radiobutton(data_tab, text='Specify location', variable=selection_radio, value='spec_loc')
specific_location_radio_btn.grid(row=5, column=2)

room_size_radio_selection = tk.StringVar()
room_size_radio_s = Radiobutton(data_tab, text='Small', variable=room_size_radio_selection, value='S')
room_size_radio_s.grid(row=6, column=1)
room_size_radio_m = Radiobutton(data_tab, text='Medium', variable=room_size_radio_selection, value='M')
room_size_radio_m.grid(row=6, column=2)
room_size_radio_l = Radiobutton(data_tab, text='Large', variable=room_size_radio_selection, value='L')
room_size_radio_l.grid(row=6, column=3)

selection_radio.trace(mode='w', callback=selectionChanged)

start_gathering_btn = Button(data_tab, text='Gather data', command=collectData)
start_gathering_btn.grid(row=7, column=1)

data_is_adapter = tk.IntVar()
data_is_adapter_checkbox = Checkbutton(data_tab, text="Is an external adapter?", variable=data_is_adapter)
data_is_adapter_checkbox.grid(row=1, column=2)

file_name_label.grid_remove()
file_name.grid_remove()
add_file_btn.grid_remove()
room_size_label.grid_remove()
room_size.grid_remove()
room_size_radio_s.grid_remove()
room_size_radio_m.grid_remove()
room_size_radio_l.grid_remove()
specific_location_label.grid_remove()
specific_location.grid_remove()

## Locating tab content
locating_interface_dropdown = tk.StringVar()
locating_interface_dropdown_menu = ttk.Combobox(locating_tab, textvariable=locating_interface_dropdown, values=available_interfaces, justify='center',  width=30)
locating_interface_dropdown_menu.grid(row=0, columnspan=3)

locating_is_adapter = tk.IntVar()
Checkbutton(locating_tab, text="Is an external adapter?", variable=locating_is_adapter).grid(row=1, column=1)

start_locating_btn = Button(locating_tab, text='Locate', command=startLocating)
start_locating_btn.grid(row=2, column=1)

if settings.USERNAME:
    user.insert(0, settings.USERNAME)
if settings.PASSWORD:
    db_pw.insert(0, settings.PASSWORD)
if settings.HOST:
    host.insert(0, settings.HOST)
if settings.DATABASE:
    db_table.insert(0, settings.DATABASE)
if settings.SUDO_PW:
    sudo_pw.insert(0, settings.SUDO_PW)

if __name__ == "__main__":
    window.mainloop()
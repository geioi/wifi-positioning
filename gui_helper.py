import tkinter as tk
import tkinter.scrolledtext as scrolledtext

console_area = None
buttons_frame = None
confirmation_value = None

def printToConsole(string):
    console_area.configure(state='normal')
    console_area.insert(tk.END, string)
    console_area.configure(state='disabled')

def createConsoleArea(master):
    global console_area

    console_label = tk.Label(master, text='Logging and debugging area: ')
    console_label.grid(row=3, sticky='w', padx=10)

    console_area = scrolledtext.ScrolledText(master, wrap='word')
    console_area.grid(row=4, sticky='sew', padx=10)
    console_area.configure(state='disabled')

def clearConsoleArea():
    console_area.configure(state='normal')
    console_area.delete(1.0, tk.END)
    console_area.configure(state='disabled')

def askConfirmation(master):
    global buttons_frame, confirmation_value
    buttons_frame.grid()
    master.wait_variable(confirmation_value)
    buttons_frame.grid_remove()
    return confirmation_value.get()

def createButtonsFrame(master):
    global buttons_frame, confirmation_value
    buttons_frame = tk.Frame(master)
    confirmation_value = tk.StringVar()
    confirm_btn = tk.Button(buttons_frame, text='Continue', command=lambda: confirmation_value.set(''))
    abort_btn = tk.Button(buttons_frame, text='Abort', command=lambda: confirmation_value.set('Abort'))
    confirm_btn.grid(row=1, column=0)
    abort_btn.grid(row=1, column=1)

    note_label = tk.Label(buttons_frame, text='If continue button is stuck for longer than a few minutes, it is advisable to abort process')
    note_label.grid(row=0, columnspan=2)

    buttons_frame.grid(row=2)

    buttons_frame.grid_remove()
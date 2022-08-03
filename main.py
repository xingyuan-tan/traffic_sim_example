import tkinter as tk

from configuration import config
from client import Client

SUMO_BINARY = config['main']['SUMO_BINARY']
SUMO_CFG = config['main']['SUMO_CFG']
TS = config['main']['TIME_STEP']

list_road = [   "North",
                "South",
                "East",
                "West"]




def main(sumocfg=SUMO_CFG, egoID="veh0"):

    root = tk.Tk()
    root.geometry('600x400')

    Client(root, sumocfg, egoID)

    start_road = tk.StringVar(root)
    start_road.set("")  # default value

    end_road = tk.StringVar(root)
    end_road.set("")  # default value

    end_widget = tk.OptionMenu(root, end_road, *list_road)
    start_widget = tk.OptionMenu(root, start_road, *list_road)

    start_widget.config(width=30)
    end_widget.config(width=30)

    start_widget.place(x=330, y=30, anchor='center')
    end_widget.place(x=330, y=50, anchor='n')

    tk.Label(text="Start").place(x=160, y=30, anchor='w')
    tk.Label(text="End").place(x=160, y=65, anchor='w')

    add_btn = tk.Button(root, text='ADD', bd='5', height='5', width='10',
                         command=lambda: Client.add_vehicle(start_road.get(),end_road.get()))
    stop_btn = tk.Button(root, text='STOP', bd='5', height='5', width='10',
                     command=lambda: Client.simple_instr('stop'))
    pause_btn = tk.Button(root, text='PAUSE', bd='5', height='5', width='10',
                     command=lambda: Client.simple_instr('pause'))
    play_btn = tk.Button(root, text='PLAY', bd='5', height='5', width='10',
                     command=lambda: Client.simple_instr('play'))

    add_btn.place(x=200, y=200, anchor='center')
    stop_btn.place(x=400, y=200, anchor='center')
    pause_btn.place(x=400, y=320, anchor='center')
    play_btn.place(x=200, y=320, anchor='center')

    root.mainloop()

main()

# if len(sys.argv) < 3:
#     main(*sys.argv[1:])
# else:
#     print("racing.py <sumocfg> [<egoID>]")

import traci
import sys
import threading
import queue
import os

from configuration import config

VERBOSE = config['main'].getboolean('VERBOSE')
SUMO_BINARY = config['main']['SUMO_BINARY']
TS = config['main']['TIME_STEP']

def print_info(traci_obj):
    vehicles = traci_obj.vehicle.getIDList()

    for i in range(0, len(vehicles)):
        x, y = traci.vehicle.getPosition(vehicles[i])
        coord = [x, y]
        lon, lat = traci.simulation.convertGeo(x, y)
        gpscoord = [lon, lat]

        sim_time = traci.simulation.getTime()

        print("Vehicle: ", vehicles[i], " at datetime: ", sim_time)
        print(vehicles[i], " >>> Position: ", coord, " | GPS Position: ", gpscoord, " |", \
              " Speed: ", round(traci.vehicle.getSpeed(vehicles[i]) * 3.6, 2), "km/h |", \
              # Returns the id of the edge the named vehicle was at within the last step.
              " EdgeID of veh: ", traci.vehicle.getRoadID(vehicles[i]), " |", \
              # Returns the id of the lane the named vehicle was at within the last step.
              " LaneID of veh: ", traci.vehicle.getLaneID(vehicles[i]), " |", \
              # Returns the distance to the starting point like an odometer.
              " Distance: ", round(traci.vehicle.getDistance(vehicles[i]), 2), "m |", \
              # Returns the angle in degrees of the named vehicle within the last step.
              " Vehicle orientation: ", round(traci.vehicle.getAngle(vehicles[i]), 2), "deg |", \
              # Return list of upcoming traffic lights [(tlsID, tlsIndex, distance, state), ...]
              " Upcoming traffic lights: ", traci.vehicle.getNextTLS(vehicles[i]), \
              )





if 'SUMO_HOME' not in os.environ:
    sys.exit("please declare environment variable 'SUMO_HOME'")
else:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

class Client:

    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """

    eventQueue = queue.Queue()

    def __init__(self, master, sumocfg, egoID):
        self.master = master
        self.sumocfg = sumocfg
        self.egoID = egoID
        self.running = True

        self.thread = threading.Thread(target=self.workerThread)
        self.thread.start()
        # Start the periodic call in the GUI to see if it can be closed
        self.periodicCall()

    @classmethod
    def simple_instr(cls, instr):
        cls.eventQueue.put((instr, None))

    @classmethod
    def add_vehicle(cls, start, end):
        if (start == "") or (end == ""):
            print("Empty selection")
        elif start == end:
            print("Start and end is the same")
        else:
            cls.eventQueue.put(("add", "a_" + start + end))

    def periodicCall(self):
        if not self.running:
            print("SHUTTING DOWN TKINTER and THREAD")
            self.master.destroy()
            self.thread.join()
        self.master.after(100, self.periodicCall)

    def workerThread(self):
        try:
            print("STARTING TRACI")
            traci.start([SUMO_BINARY, "-c", self.sumocfg,
                         "--lateral-resolution", "0.32",
                         "--collision.action", "warn",
                         "--step-length", str(TS),
                         "--quit-on-end", "true",
                         "--start", "true"
                         ])
            traci.simulationStep()
            total_veh = 0
            pause = True
            stop = False
            while not stop:
                try:
                    if self.eventQueue.qsize() == 0:
                        pass
                    while self.eventQueue.qsize():
                        try:
                            msg = self.eventQueue.get(0)
                            # if len(msg) == 1:
                            #     direction = msg
                            #     val = None
                            # else:
                            direction, val = msg

                            if direction == 'add':
                                veh_id = "add"+str(total_veh)
                                traci.vehicle.add(veh_id, val, departPos=0)
                                total_veh += 1
                                if VERBOSE:
                                    print("Added "+veh_id+" for "+val)

                            if direction == 'stop':
                                print("STOPPING")
                                self.running = False
                                stop = True

                            if direction == 'pause':
                                pause = True

                            if direction == 'play':
                                pause = False

                        except queue.Empty:
                            pass
                    if not pause:
                        print_info(traci)
                        traci.simulationStep()
                except traci.TraCIException:
                    print("TRACI EXCEPTION")
                    pass

            print("CLOSING TRACI")
            traci.close()
        except traci.FatalTraCIError:
            print("TRACI FATAL")
            pass

        print("STOPPED")




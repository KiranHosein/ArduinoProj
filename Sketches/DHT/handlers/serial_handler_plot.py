import serial
import ast
import threading
import time
import os
import pandas as pd
import signal

class SafeList:
    """Class for a persistent dynamic list that 
    can be accessed while it is being appended."""

    def __init__(self):
        self._list = []
        self._lock = threading.Lock()

    def add_item(self, item):
        """Append an item to the list."""
        with self._lock:
            self._list.append(item)

    def get_list(self) -> list:
        """Return the entire list."""
        with self._lock:
            return list(self._list)

    def get_last_n_items(self, n: int) -> list:
        """Return the last n items of the list."""
        with self._lock:
            return self._list[-n:]

    def set_list(self, new_list: list):
        """Set the value of the list."""
        with self._lock:
            self._list = new_list


def readserial(comport: str, baudrate: int, data_store: SafeList, n_last: int):
    """Read from the serial port and store the last n items in data_store."""
    ser = serial.Serial(comport, baudrate, timeout=0.1)
    start_time = time.time()

    while True:
        data = ser.readline().decode().strip()
        if data and data[0] == "{" and data[-1] == "}":
            try:
                r_dict = ast.literal_eval(data) #convert a str representation of a dict to dict
                current_time = round(time.time() - start_time)
                r_dict["Time"] = current_time #add a time for each dict entry
                data_store.add_item(r_dict)
                # Keep only the last n items of the dict
                if len(data_store.get_list()) > n_last:                 
                    data_store.set_list(data_store.get_last_n_items(n_last))
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing data: {data} - {e}")
        time.sleep(0.1)  # Adjust to control read frequency


def update_dataframe(data_store: SafeList) -> pd.DataFrame:
    """Create a dataframe based on the persisted data input."""
    current_data = data_store.get_list()
    df = pd.DataFrame(current_data)
    return df


def process_data(data_store: SafeList):
    """Example function to read and process data from the SafeList.
    And show that the dynamic list can be accessed in a different thread."""
    while True:
        # generate a new dataframe based on new serial inputs
        df_update = update_dataframe(data_store)
        print(df_update)

        time.sleep(1)  # Simulate processing delay


def collect_data(data_store: SafeList):
    """Data collection function to save 
    timeseries data after a set number of entries."""
    counter = 0
    checkpoint = 100
    while True:
        if data_store and len(data_store.get_list())>=1:
            #print(data_store.get_list())
            if len(data_store.get_list()) == 500:
                df_update = update_dataframe(data_store)
                #print(data_store.get_list())
                print(df_update)
                df_update.to_csv("anom_time_series.csv")
            elif len(data_store.get_list()) % checkpoint == 0:
                #print(print(data_store.get_list()))
                checkpoint_data = data_store.get_last_n_items(n=checkpoint)
                df_c = pd.DataFrame(checkpoint_data)
                df_c.to_csv(f"anom_time_series_checkpoint_{counter}.csv")
                counter = counter + checkpoint
                #print(checkpoint_data)
                print(df_c)
                print(counter)
            elif len(data_store.get_list()) % 25 == 0:
                print(print(data_store.get_list()))
            elif len(data_store.get_list()) > 5000:
                os.kill(os.getpid(), signal.SIGINT)
            time.sleep(1)  # Simulate processing delay




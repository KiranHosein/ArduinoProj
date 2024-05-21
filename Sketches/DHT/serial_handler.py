import serial
import ast
import threading
import time

import streamlit as st
import pandas as pd


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

    while True:
        data = ser.readline().decode().strip()
        if data and data[0] == "{" and data[-1] == "}":
            try:
                r_dict = ast.literal_eval(data)
                data_store.add_item(r_dict)
                if len(data_store.get_list()) > n_last:
                    # Keep only the last n items
                    data_store.set_list(data_store.get_last_n_items(n_last))
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing data: {data} - {e}")
        time.sleep(0.1)  # Adjust as needed to control read frequency


def update_display(data):
    """Update the streamlit elements upon new data read in."""
    df = pd.DataFrame(data)
    return df


def process_data(data_store: SafeList):
    """Example function to read and process data from the SafeList.
    And show that the dynamic list can be accessed."""
    while True:
        current_data = data_store.get_list()
        # print(f"Current list state: {current_data}")
        test = update_display(current_data)
        print(test)
        time.sleep(1)  # Simulate processing delay

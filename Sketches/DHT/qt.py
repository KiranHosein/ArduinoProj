import serial
import ast
import threading
import time

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation


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
                r_dict = ast.literal_eval(data)
                current_time = round(time.time() - start_time)
                r_dict["Time"] = current_time
                data_store.add_item(r_dict)
                if len(data_store.get_list()) > n_last:
                    # Keep only the last n items
                    data_store.set_list(data_store.get_last_n_items(n_last))
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing data: {data} - {e}")
        time.sleep(0.1)  # Adjust as needed to control read frequency


def update_plot(i, data_store, line, ax):
    """Update the plot with new data."""
    data = data_store.get_list()
    if data:
        df = pd.DataFrame(data)
        ax.clear()
        ax.plot(df['Time'], df['T'], label='Temperature')
        ax.plot(df['Time'], df['H'], label='Humidity')
        ax.legend(loc='upper right')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Value')
        ax.set_title('Real-Time Temperature and Humidity')


def main():
    port = 'COM3'
    baud_rate = 9600
    n_last = 10  # Keep the last 10 items in the list

    safe_list = SafeList()

    # Start the serial reading thread
    serial_thread = threading.Thread(
        target=readserial, args=(port, baud_rate, safe_list, n_last))
    serial_thread.daemon = True
    serial_thread.start()

    # Set up the plot
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'r-')

    # Use FuncAnimation to update the plot
    ani = animation.FuncAnimation(
        fig, update_plot, fargs=(safe_list, line, ax), interval=1000)

    plt.show()


if __name__ == "__main__":
    main()

import serial
import ast
import threading
import time
import pandas as pd
import numpy as np

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


# Define functions for preprocessing, sequence creation, and streaming prediction
def preprocess_data(data_store: SafeList, t_mean_train, t_std_train, h_mean_train, h_std_train):
    if data_store and len(data_store.get_list()) > 2:
        df = update_dataframe(data_store)
        df["T_standardscaled"] = (df["T"] - t_mean_train) / t_std_train 
        df["H_standardscaled"] = (df["H"] - h_mean_train) / h_std_train 
        print(df)
        return df
    return None

def create_sequences(values, time_steps=60):
    output = []
    for i in range(len(values) - time_steps + 1):
        output.append(values[i : (i + time_steps)])
    return np.stack(output) if output else np.empty((0, time_steps, values.shape[1]))


def predict_on_streaming_data(model, data_store, t_mean_train, t_std_train, h_mean_train, h_std_train, threshold):
    while True:
        preprocessed_data = preprocess_data(data_store, t_mean_train, t_std_train, h_mean_train, h_std_train)
        if preprocessed_data is not None:
            sequences = create_sequences(preprocessed_data[["H_standardscaled"]].values)
            print(sequences)
            if sequences.size > 0:
                predictions = model.predict(sequences)
                mae_loss = np.mean(np.abs(predictions - sequences), axis=1)
                mae_loss = mae_loss.reshape((-1))
                anomalies = mae_loss > threshold
                if any(anomalies):
                    print("Anomaly detected!")
                    print("Indices of anomaly samples: ", np.where(anomalies))
                else:
                    print("No anomaly detected.")
        time.sleep(1)  # Simulate processing delay






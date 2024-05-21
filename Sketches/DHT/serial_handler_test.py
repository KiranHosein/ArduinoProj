"""Handler file to convert data input from serial into python dict."""
import serial
import ast


def readserial(comport: str, baudrate: int, data_store: list, n_last: int):
    """Expecting a dict-like object from the serial port. 
    Specify a port, rate, and a list for data storage. 
    The list will be appended to and the last n number of in the list will be kept.
    Any previous items will be overwritten. """

    # 1/timeout is the frequency at which the port is read
    ser = serial.Serial(comport, baudrate, timeout=0.1)

    while True:
        data = ser.readline().decode().strip()
        if data and data[0] == "{" and data[-1] == "}":
            r_dict = ast.literal_eval(data)
            data_store.append(r_dict)
            if len(data_store) > n_last:
                data_store = data_store[-n_last:]
            # print(data_store)


# data_store = []
# n_last = 3
# port = 'COM3'
# baud_rate = 9600

# readserial(port, baud_rate, data_store, n_last)

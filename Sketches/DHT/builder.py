"""Provide functions for handling streaming data from serial port."""
import serial

# Set up the serial connection (replace 'COM3' with your serial port and '9600' with your baud rate)
ser = serial.Serial('COM3', 9600)

# Read data from the serial port


def read_from_serial() -> None:
    """Read data from serial port and if found return raw data."""
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        return data
    return None


def process_data(data):
    """Handle the data read in from serial."""
    try:
        out_dict = {"temp": ""}
        if data[0] == "T":
            out_dict["temp"] = float(data[2:])
        # elif data[0] == "H":
        #     out_dict["hum"] = float(data[2:])
        return out_dict
    except ValueError:
        return None

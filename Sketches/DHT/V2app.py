import serial
import streamlit as st
import pandas as pd
import time

# Configuration for the serial port
port = 'COM3'
baud_rate = 9600

try:
    # Open serial port
    # Set a timeout to prevent blocking
    ser = serial.Serial(port, baud_rate, timeout=1)
except serial.SerialException as e:
    st.error(f"Could not open port {port}: {e}")
    st.stop()

# Streamlit app title
st.title("Real-Time Streaming Demo")

# Initialize data storage
data = {"Temperature": None, "Humidity": None}

# Function to read from the serial port


def read_serial():
    try:
        if ser.in_waiting > 0:  # Check if there is data in the buffer
            line = ser.readline().decode('utf-8').strip()
            if line and (line.startswith("T") or line.startswith("H")):
                if line[0] == "T":
                    data["Temperature"] = line[2:]
                elif line[0] == "H":
                    data["Humidity"] = line[2:]
                return True
    except serial.SerialException as e:
        st.error(f"Serial error: {e}")
        ser.close()
    return False


# Placeholder for the dataframe
placeholder = st.empty()

try:
    while True:
        if read_serial():
            df = pd.DataFrame([
                {"Metric": "Temperature", "Value": data["Temperature"]},
                {"Metric": "Humidity", "Value": data["Humidity"]}
            ])
            placeholder.dataframe(df, use_container_width=True)
        # time.sleep(1)  # Sleep for a second before updating
except KeyboardInterrupt:
    st.stop()
finally:
    ser.close()

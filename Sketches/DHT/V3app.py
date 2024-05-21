import serial
import streamlit as st
import pandas as pd
import numpy as np
import time

# Configuration for the serial port
port = 'COM3'
baud_rate = 9600

st.set_page_config(page_title="Data Streaming Demo",
                   layout="wide", initial_sidebar_state="auto")

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
data = {"Time": [], "Temperature": [], "Humidity": []}
start_time = time.time()


def read_serial() -> bool:
    """Read in information from arduino via the serial connection. 
    Append to the internal data storage if data available."""

    if ser.in_waiting > 0:  # Check if there is data in the buffer
        line = ser.readline().decode('utf-8').strip()
        current_time = round(time.time() - start_time)
        if line:
            if line.startswith("T"):
                temp_value = float(line[2:])
                data["Time"].append(current_time)
                data["Temperature"].append(temp_value)
                data["Humidity"].append(np.nan)  # Placeholder for humidity
            elif line.startswith("H"):
                hum_value = float(line[2:])
                data["Time"].append(current_time)
                data["Temperature"].append(np.nan)  # Placeholder for temp
                data["Humidity"].append(hum_value)
    return data


# Placeholder for the dataframe and charts
col1, col2 = st.columns([0.25, 0.75])
with col1:
    df_placeholder = st.empty()
with col2:
    chart_placeholder = st.empty()


def update_display(data):
    """Update the streamlit elements upon new data read in."""
    # read last row of each metric
    time_last = data["Time"]
    temp_last = data["Temperature"]
    hum_last = data["Humidity"]

    df = pd.DataFrame(data)

    # Forward fill to align NaN values properly
    df['Temperature'] = df['Temperature'].ffill()
    df["Humidity"] = df['Humidity'].ffill()

    # Update the data table
    df_placeholder.dataframe(df)

    # Update the line chart
    chart_placeholder.line_chart(df.set_index(
        "Time"))

    st.write(time_last)
    st.write(temp_last)
    st.write(hum_last)


try:
    while True:
        if read_serial():
            update_display(data)

except KeyboardInterrupt:
    st.stop()
finally:
    ser.close()

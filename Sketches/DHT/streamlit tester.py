import serial_handler
import time
import threading

import streamlit as st
import pandas as pd


safe_list = serial_handler.SafeList()
port = 'COM3'
baud_rate = 9600
n_last = 5

# streamlit config
st.set_page_config(page_title="Data Streaming Demo",
                   layout="wide", initial_sidebar_state="auto")

st.title("Real-Time Streaming Demo")

# Placeholder for the dataframe and charts
col1, col2 = st.columns([0.25, 0.75])
with col1:
    df_placeholder = st.empty()
with col2:
    chart_placeholder = st.empty()

# Start the serial reading thread
serial_thread = threading.Thread(
    target=serial_handler.readserial, args=(port, baud_rate, safe_list, n_last))
serial_thread.daemon = True
serial_thread.start()

# Start the data processing thread
processing_thread = threading.Thread(
    target=serial_handler.process_data, args=(safe_list, df_placeholder, chart_placeholder))
processing_thread.daemon = True
processing_thread.start()


try:
    while True:
        time.sleep(0.1)  # Keep the main thread running
except KeyboardInterrupt:
    print("Stopping threads.")

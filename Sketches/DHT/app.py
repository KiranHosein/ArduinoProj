import streamlit as st
import time
import threading
import pandas as pd

import builder

# Global buffer for storing data
data_buffer = []

# Function to read serial data in a separate thread


def read_serial_data():
    global data_buffer
    while True:
        data = builder.read_from_serial()
        if data:
            processed_data = builder.process_data(data)
            if processed_data is not None:
                data_buffer.append(processed_data)
                if len(data_buffer) > 50:
                    data_buffer.pop(0)
        time.sleep(0.1)


# Start the serial reading in a separate thread
thread = threading.Thread(target=read_serial_data)
thread.daemon = True
thread.start()

# Streamlit app to display the data
st.title('Real-Time Data Dashboard')

# Main loop to update the Streamlit app
while True:
    st.write("hello")
    if data_buffer:
        st.line_chart(pd.DataFrame(data_buffer, columns=['Value']))
    time.sleep(1)

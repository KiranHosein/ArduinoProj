from handlers import serial_handler
import time
import threading

#Define variables for connection
port = 'COM3'
baud_rate = 9600

#Define variables for storage and readout
safe_list = serial_handler.SafeList()
n_last = 10

# Start the serial reading thread
serial_thread = threading.Thread(
    target=serial_handler.readserial, args=(port, baud_rate, safe_list, n_last))
serial_thread.daemon = True
serial_thread.start()

# Start the data processing thread
processing_thread = threading.Thread(
    target=serial_handler.process_data, args=(safe_list,))
processing_thread.daemon = True
processing_thread.start()

try:
    while True:
        time.sleep(0.1)  # Keep the main thread running
except KeyboardInterrupt:
    print("Stopping threads.")

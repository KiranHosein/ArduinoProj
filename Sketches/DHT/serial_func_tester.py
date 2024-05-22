import Sketches.DHT.serial_handler as serial_handler
import time
import threading


safe_list = serial_handler.SafeList()
port = 'COM3'
baud_rate = 9600
n_last = 5

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

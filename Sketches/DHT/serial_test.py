"""Tester file to check serial connection in python."""
import serial

port = 'COM3'
baud_rate = 9600

# Open serial port
ser = serial.Serial(port, baud_rate)

# Check if the port is open
if ser.is_open:
    print(f"Successfully connected to {port}")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line[0] == "T":
            print(f"Received temperature: {line[2:]} C")
        else:
            print(f"Received humidity: {line[2:]}%\n")

except KeyboardInterrupt:
    print("Exiting the program.")
finally:
    ser.close()

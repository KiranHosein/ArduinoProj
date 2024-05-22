import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from handlers import serial_handler_plot

# Initialize the SafeList and other parameters
safe_list = serial_handler_plot.SafeList()
port = 'COM3'
baud_rate = 9600
n_last = 10 #get last 10 items i.e. last 10 seconds of data

# Start the serial reading thread
serial_thread = threading.Thread(
    target=serial_handler_plot.readserial, args=(port, baud_rate, safe_list, n_last))
serial_thread.daemon = True
serial_thread.start()

# Start the data processing thread - currently supplementary
processing_thread = threading.Thread(
    target=serial_handler_plot.process_data_plot, args=(safe_list,))
processing_thread.daemon = True
processing_thread.start()


# Create a plot
fig = plt.figure(figsize=(6,4))
axes = fig.add_subplot(1,1,1)
plt.title("Arduino sensors over time.")

def animate(i): #i is the current frame
    if safe_list and len(safe_list.get_list()) > 1:
        #latest_data = safe_list.get_list()[-1]  # Get the latest data
        x_data = [entry['Time'] for entry in safe_list.get_list()]
        y_data_1 = [entry['H'] for entry in safe_list.get_list()]
        y_data_2 = [entry['T'] for entry in safe_list.get_list()]
        
        plt.xlim(i-n_last,i+1)
        axes.set_ylim(0,100)
        line1, = axes.plot(x_data,y_data_1, scaley=True, scalex=True, color="blue")
        line1.set_label('Humidity (%)')
        line2, = axes.plot(x_data,y_data_2, scaley=True, scalex=True, color="red")
        line2.set_label('Temp (C)')
        axes.legend(handles=[line1, line2])


anim = animation.FuncAnimation(fig, animate, interval=1000)

plt.xlabel('Time (s)')
plt.ylabel('Sensors')
plt.show()

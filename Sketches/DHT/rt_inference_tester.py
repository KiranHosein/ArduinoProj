import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from handlers import serial_handler_rt
import keras
import json


# Load the model
model = keras.saving.load_model(r'./Anomaly_Detection/trained_model.keras')
# Load mean, std, and threshold values from a JSON file
with open(r'./Anomaly_Detection/scaling_thresholds.json', 'r') as f:
    data = json.load(f)

t_mean_train = data['t_mean_train']
t_std_train = data['t_std_train']
h_mean_train = data['h_mean_train']
h_std_train = data['h_std_train']
threshold = data['threshold']

# Initialize the SafeList and other parameters
safe_list = serial_handler_rt.SafeList()
port = 'COM3'
baud_rate = 9600
n_last = 120 #get last 10 items i.e. last 10 seconds of data

# Start the serial reading thread
serial_thread = threading.Thread(
    target=serial_handler_rt.readserial, args=(port, baud_rate, safe_list, n_last))
serial_thread.daemon = True
serial_thread.start()

# Start the data collecting thread 
processing_thread = threading.Thread(
    target=serial_handler_rt.predict_on_streaming_data, args=(model, safe_list, t_mean_train, t_std_train, h_mean_train, h_std_train, threshold))
processing_thread.daemon = True
processing_thread.start()


# Create a plot
fig = plt.figure(figsize=(6,4))
axes = fig.add_subplot(1,1,1)
# major_ticks = np.arange(-10, 121, 20)
# minor_ticks = np.arange(-10, 121, 10)
# axes.set_yticks(major_ticks)
# axes.set_yticks(minor_ticks, minor=True)

plt.title("Arduino sensors over time.")

def animate(i): #i is the current frame
    if safe_list and len(safe_list.get_list()) > 1:
        #latest_data = safe_list.get_list()[-1]  # Get the latest data
        x_data = [entry['Time'] for entry in safe_list.get_list()]
        y_data_1 = [entry['H'] for entry in safe_list.get_list()]
        y_data_2 = [entry['T'] for entry in safe_list.get_list()]
        
        plt.xlim(i-30, i+1)
        axes.set_ylim(-20,100)
        line1, = axes.plot(x_data,y_data_1, scaley=True, scalex=True, color="blue", linestyle = "dotted")
        line1.set_label('Humidity (%)')
        line2, = axes.plot(x_data,y_data_2, scaley=True, scalex=True, color="red")
        line2.set_label('Temp (C)')
        axes.legend(handles=[line1, line2])


anim = animation.FuncAnimation(fig, animate, interval=1000,cache_frame_data=False)

plt.xlabel('Time (s)')
plt.ylabel('Sensors')
plt.grid()
plt.show()

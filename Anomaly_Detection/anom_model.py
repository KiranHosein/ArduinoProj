import numpy as np
import pandas as pd
import keras
from keras import layers
import json

custom_objects = {
    "mse": keras.losses.MeanSquaredError()
}

# data read in
df_th = pd.read_csv(r'ArduinoProj/time_series.csv')
df_th.head()
df_th.drop(columns=["Unnamed: 0"], inplace=True)


# anomaly read in
df_tha = pd.read_csv(r'ArduinoProj/anom_time_series_try2.csv')
df_tha.head()
df_tha.drop(columns=["Unnamed: 0"], inplace=True)

#standard scaling the training set
t_mean_train = df_th["T"].mean()
t_std_train = df_th["T"].std()
h_mean_train = df_th["H"].mean()
h_std_train = df_th["H"].std()

df_th["T_standardscaled"] = (df_th["T"] - t_mean_train) / t_std_train 
df_th["H_standardscaled"] = (df_th["H"] - h_mean_train) / h_std_train 

df_tha["T_standardscaled"] = (df_tha["T"] - t_mean_train) / t_std_train 
df_tha["H_standardscaled"] = (df_tha["H"] - h_mean_train) / h_std_train 

#running model only on humidity readings only
df_train = df_th[["H_standardscaled"]] 
df_test = df_tha[["H_standardscaled"]] # test on anomalous data

# Generated training sequences for use in the model.
TIME_STEPS = 60
def create_sequences(values, time_steps=TIME_STEPS):
    output = []
    for i in range(len(values) - time_steps + 1):
        output.append(values[i : (i + time_steps)])
    return np.stack(output)

x_train = create_sequences(df_train.values)

model = keras.Sequential(
    [
        layers.Input(shape=(x_train.shape[1], x_train.shape[2])),
        layers.Conv1D(
            filters=32,
            kernel_size=5,
            padding="same",
            strides=2,
            activation="relu",
        ),
        layers.Dropout(rate=0.2),
        layers.Conv1D(
            filters=16,
            kernel_size=5,
            padding="same",
            strides=1,
            activation="relu",
        ),
        layers.Conv1DTranspose(
            filters=16,
            kernel_size=5,
            padding="same",
            strides=2,
            activation="relu",
        ),
        layers.Dropout(rate=0.1),
        layers.Conv1DTranspose(
            filters=32,
            kernel_size=5,
            padding="same",
            strides=1,
            activation="relu",
        ),
        layers.Conv1DTranspose(filters=1, kernel_size=4, padding="same")
    ]
)

model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss="mse")
model.summary()

history = model.fit(
    x_train,
    x_train,
    epochs=50,
    batch_size=250,
    validation_split=0.1,
    callbacks=[
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, mode="min")
    ],
)


# Get train MAE loss.
x_train_pred = model.predict(x_train)
train_mae_loss = np.mean(np.abs(x_train_pred - x_train), axis=1)

# Get reconstruction loss threshold.
threshold = np.max(train_mae_loss)

# save trained model and data to JSON
model.save('ArduinoProj/Anomaly_Detection/trained_model.keras')
data = {
    't_mean_train': t_mean_train,
    't_std_train': t_std_train,
    'h_mean_train': h_mean_train,
    'h_std_train': h_std_train,
    'threshold': threshold
}

with open('ArduinoProj/Anomaly_Detection/scaling_thresholds.json', 'w') as f:
    json.dump(data, f)


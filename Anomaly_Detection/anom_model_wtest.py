import numpy as np
import pandas as pd
import keras
from keras import layers
from matplotlib import pyplot as plt

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

# create test set
x_test = create_sequences(df_test.values)

# Get test MAE loss.
x_test_pred = model.predict(x_test)
test_mae_loss = np.mean(np.abs(x_test_pred - x_test), axis=1)
test_mae_loss = test_mae_loss.reshape((-1))

# Detect all the samples which are anomalies.
anomalies = test_mae_loss > threshold
print("Number of anomaly samples: ", np.sum(anomalies))
print("Indices of anomaly samples: ", np.where(anomalies))

# data i is an anomaly if samples [(i - timesteps + 1) to (i)] are anomalies
anomalous_data_indices = []
for data_idx in range(TIME_STEPS - 1, len(df_test) - TIME_STEPS + 1):
#for data_idx in range(0, len(df_test) - 1):
    if np.all(anomalies[data_idx - TIME_STEPS + 1 : data_idx]):
        anomalous_data_indices.append(data_idx)

df_subset = df_test.iloc[anomalous_data_indices]
fig, ax = plt.subplots()
df_test.plot(legend=False, ax=ax)
df_subset.plot(legend=False, ax=ax, color="r")
plt.show()
from tensorflow import keras
import pandas as pd

data = pd.read_csv('ProcessedMeasurements.csv')
train_data = data.sample(frac=0.8, random_state=0)
test_data = data.drop(train_data.index)
train_labels = train_data.pop('PRCP')
test_labels = test_data.pop('PRCP')
train_stats = train_data.describe()
train_stats = train_stats.transpose()

def norm(x):
  return (x - train_stats['mean']) / train_stats['std']

#train_data = norm(train_data)
#test_data = norm(test_data)

def build_model():
    model = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=[len(train_data.keys())]),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(1)
    ])

    optimizer = keras.optimizers.RMSprop(0.001)

    model.compile(loss='mae',
                optimizer=optimizer,
                metrics=['mae', 'mse'])
    return model

model = build_model()

history = model.fit(
  train_data, train_labels,
  epochs=4, validation_split = 0.2)

test_predictions = model.predict(test_data).flatten()
print('MSE for this model:', keras.losses.MSE(test_labels, test_predictions))
print('MSE for simplest model:', keras.losses.MSE(test_labels, test_data['PRCP_1_3']))
print('MAE for this model:', keras.losses.MAE(test_labels, test_predictions))
print('MAE for simplest model:', keras.losses.MAE(test_labels, test_data['PRCP_1_3']))
model.save(r'Models')
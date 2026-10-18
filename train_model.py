import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
import os

print("--- Step 1: Loading Dataset ---")
# Load the CSV file
df = pd.read_csv('rssi_dataset.csv')

# Extract inputs (RSSI) and outputs (Distance)
X = df['RSSI'].values
y = df['Distance'].values

# Split data: 80% for training the brain, 20% for testing its accuracy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("--- Step 2: Building Neural Network ---")
# The 16 -> 8 Funnel Architecture with ReLU
model = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu', input_shape=(1,)),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(1) # Final output node for distance
])

# Compile the model using Mean Absolute Error (MAE) to measure its mistakes
model.compile(optimizer='adam', loss='mae')

print("--- Step 3: Training the AI ---")
# Train the model for 300 cycles (epochs)
model.fit(X_train, y_train, epochs=300, validation_data=(X_test, y_test), verbose=1)

print("\n--- Step 4: Compressing to TinyML ---")
# Convert the massive TensorFlow model into a lightweight TensorFlow Lite model
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the raw .tflite file
with open('rssi_model.tflite', 'wb') as f:
    f.write(tflite_model)

print("--- Step 5: Generating C++ Array for ESP32 ---")
# Convert the binary TFLite model into a C++ hex array for the Arduino IDE
hex_array = ', '.join([f'0x{byte:02x}' for byte in tflite_model])
c_code = f"""// Auto-generated TinyML Model for ESP32
const unsigned char rssi_model_tflite[] = {{
    {hex_array}
}};
const int rssi_model_tflite_len = {len(tflite_model)};
"""

# Save to a header file
with open('model.h', 'w') as f:
    f.write(c_code)

print("\n✅ Success! Your Edge AI model is fully trained.")
print("Generated 'model.h' - You can now include this directly in your ESP32 project!")
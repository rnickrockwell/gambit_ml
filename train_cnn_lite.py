import os
import tensorflow as tf

# Load the TensorFlow model
model_path = 'models/1DCNN.keras'
model = tf.keras.models.load_model(model_path)

# Convert the model to TFLite format
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the TFLite model to a file
tflite_model_path = 'models/1DCNN.tflite'
with open(tflite_model_path, 'wb') as f:
    f.write(tflite_model)

print(f"Saved TFLite model to {tflite_model_path}")

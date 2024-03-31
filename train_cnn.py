import os
import numpy as np
import pandas as pd
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout

# Load and preprocess data
def load_data(data_folder):
    csv_files = [p for p in data_folder.glob('*')]
    dataframes = [pd.read_csv(file, header=None) for file in csv_files]
    concatenated_df = pd.concat(dataframes, axis=0)
    concatenated_df.reset_index(drop=True, inplace=True)
    return concatenated_df

def preprocess_data(data_df):
    X = data_df.iloc[:, :-1].values
    y = data_df.iloc[:, -1].values
    # Remap labels 9, 12, 15 to 0, 1, 2
    unique_labels = np.unique(y)
    label_mapping = {label: idx for idx, label in enumerate(unique_labels)}
    y_remapped = np.array([label_mapping[label] for label in y], dtype=int)
    X = X.reshape((X.shape[0], X.shape[1], 1))  # Reshape for CNN input
    return X, y_remapped

# Define the model
def build_model(input_shape, num_classes=3):  # Defaulting to 3 classes
    model = Sequential([
        Conv1D(filters=32, kernel_size=7, activation='relu', input_shape=input_shape),
        MaxPooling1D(pool_size=2),
        Conv1D(filters=64, kernel_size=3, activation='relu'),
        MaxPooling1D(pool_size=2),
        Flatten(),
        Dense(100, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

if __name__ == "__main__":
    # Data preparation
    data_folder = Path('training_data')
    concatenated_df = load_data(data_folder)
    X, y = preprocess_data(concatenated_df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.70, stratify=y, random_state=69)

    # Model configuration
    input_shape = (X_train.shape[1], 1)
    model = build_model(input_shape)

    # Training the model
    history = model.fit(X_train, y_train, epochs=65, batch_size=64, validation_split=0.2)

    # Evaluate the model on the test set
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f'\nTest Accuracy: {test_accuracy * 100:.2f}%')

    # Print training accuracy
    final_epoch_training_accuracy = history.history['accuracy'][-1] * 100
    print(f'Training Accuracy: {final_epoch_training_accuracy:.2f}%')

    # Save the model with a .keras extension
    models_folder = 'models'
    os.makedirs(models_folder, exist_ok=True)
    model_filename_keras = os.path.join(models_folder, '1DCNN.keras')
    model.save(model_filename_keras)
    print(f"Saved TensorFlow model as a .keras file to {model_filename_keras}")

    # Update the accuracies.json file with the CNN model's accuracies
    accuracies_file = 'accuracies.json'
    if os.path.exists(accuracies_file):
        with open(accuracies_file, 'r') as f:
            accuracies = json.load(f)
    else:
        accuracies = {}

    accuracies['1DCNN'] = {
        'Train Accuracy': final_epoch_training_accuracy,
        'Test Accuracy': test_accuracy * 100
    }

    with open(accuracies_file, 'w') as f:
        json.dump(accuracies, f, indent=4)




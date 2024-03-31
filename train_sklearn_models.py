import os
import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from joblib import dump  # Import dump for saving models
from pathlib import Path

# Ensure the 'models' folder exists
models_folder = 'models'
os.makedirs(models_folder, exist_ok=True)

# List of CSV files
training_data_folder = Path('training_data')
csv_files = [p for p in training_data_folder.glob('*')]  # Update these with your actual file paths

# Read each CSV file into a DataFrame and append it to a list
dataframes = [pd.read_csv(file, header=None) for file in csv_files]

# Concatenate all DataFrames vertically
concatenated_df = pd.concat(dataframes, axis=0)

# Reset the index of the concatenated DataFrame
concatenated_df.reset_index(drop=True, inplace=True)

# Split into features (X) and target variable (y)
# Assuming the last column is the target variable
X = concatenated_df.iloc[:, :-1].values
y = concatenated_df.iloc[:, -1].values.astype(int)  # Cast y to integers

# Split data into training and test sets, stratifying on y
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.80, stratify=y, random_state=69)

# Dictionary of models to train
models = {
    'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
    'KNeighbors': KNeighborsClassifier(),
    'GaussianNB': GaussianNB(),
    'DecisionTree': DecisionTreeClassifier(random_state=42),
    'SVM': SVC(random_state=42),
    'MLP': MLPClassifier(hidden_layer_sizes=(24,), max_iter=1000, random_state=42),
    'RandomForest': RandomForestClassifier(random_state=42),
    'GradientBoosting': GradientBoostingClassifier(random_state=42),
}

# Initialize a dictionary to store accuracies
accuracies = {}

# Train multiple models and save them
for name, model in models.items():
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions on both train and test sets
    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)
    
    # Calculate and print accuracy for both train and test sets
    train_accuracy = accuracy_score(y_train, train_predictions)
    test_accuracy = accuracy_score(y_test, test_predictions)
    
    print(f"{name}:")
    print(f"  - Train Accuracy: {train_accuracy * 100:.2f}%")
    print(f"  - Test Accuracy: {test_accuracy * 100:.2f}%\n")
    
    # Save the model to a file in the 'models' folder
    model_filename = os.path.join(models_folder, f'{name}.pkl')
    dump(model, model_filename)
    print(f"Saved {name} model to {model_filename}")
    
    # Add accuracies to the dictionary
    accuracies[name] = {
        'Train Accuracy': train_accuracy,
        'Test Accuracy': test_accuracy
    }

# Write accuracies to a JSON file
with open('accuracies.json', 'w') as f:
    json.dump(accuracies, f, indent=4)

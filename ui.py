import streamlit as st
from subprocess import run
import pandas as pd
import os
import json
import matplotlib.pyplot as plt

# Set the page layout to wide
st.set_page_config(layout="wide")

python_runtime = 'python3.10'

def record_data(target_frequency, duration):
    """Function to record data."""
    run(f'{python_runtime} game_data_recorder.py {target_frequency} {duration}'.split())
    

def train_models():
    """Function to train models."""
    run(f'{python_runtime} train_sklearn_models.py'.split())
    run(f'{python_runtime} train_cnn.py'.split())
    # Load accuracies from the JSON file
    with open('accuracies.json', 'r') as f:
        accuracies = json.load(f)
    # Create a DataFrame from the accuracies and store it in session state
    st.session_state.accuracies_df = pd.DataFrame(accuracies).T  # Transpose to have models as rows
    st.session_state.accuracies_df.rename(columns={'Train Accuracy': 'Train Accuracy (%)', 'Test Accuracy': 'Test Accuracy (%)'}, inplace=True)
    # Sort by Test Accuracy
    st.session_state.accuracies_df.sort_values(by='Test Accuracy (%)', ascending=False, inplace=True)


def launch_game(model, duration):
    """Function to launch the game."""
    if model:
        run(f'{python_runtime} predictor_queue.py {model} {duration}'.split())
    else:
        st.warning("Please select a model to launch the game.")
 

# Streamlit app layout
st.title('Gambit')

# Create a two-column layout
col1, col2 = st.columns(2)

# Data Recorder Section
with col1:
    with st.form("data_recorder_form"):
        st.subheader('Collect Data')
        col_frequency, col_duration = st.columns(2)
        with col_frequency:
            target_frequency = st.number_input("Target Frequency", value=9, min_value=1)
        with col_duration:
            duration = st.number_input("Duration (seconds)", value=25, min_value=10)
        record_button = st.form_submit_button("Record Data")

    if record_button:
        record_data(target_frequency, duration)

# Train Models Section
with col1:
    with st.form("train_models_form"):
        st.subheader('Train Models')
        train_button = st.form_submit_button("Train Models")

        if train_button:
            train_models()

        # Display the accuracies table if it exists in session state
        if 'accuracies_df' in st.session_state:
            st.session_state.accuracies_df.index.name = 'Model'
            st.table(st.session_state.accuracies_df)


# Launching the Game Section
with col2:
    with st.form("launch_game_form"):
        st.subheader('Launch the Game')
        col_model, col_duration = st.columns([3, 1])  # Allocate more space to model selection
        with col_model:
            model_list = sorted(os.listdir('models'))
            selected_model = st.selectbox("Select a Model", [None] + model_list, key="model_select")
        with col_duration:
            duration = st.number_input("Game Duration (seconds)", value=60, min_value=20, key="game_duration")
        launch_button = st.form_submit_button("Start the Game")

    if launch_button and selected_model:
        launch_game(selected_model, duration)
    elif launch_button:
        st.warning("Please select a model to launch the game.")

# Visualization Section
with col2:
    with st.form("data_visualization_form"):
        st.subheader('Frequency Spectrum Visualization')
        file_list = sorted(os.listdir('training_data'))
        if file_list:  # Check if the list is not empty
            col_plot, col_file = st.columns([1, 3])  # Allocate more space to file selection
            with col_file:
                selected_file = st.selectbox("Select a CSV File", file_list, index=None)
            with col_plot:
                st.write("")
                plot_button = st.form_submit_button("Plot Data")
            if plot_button and selected_file:
                df = pd.read_csv(f'training_data/{selected_file}')
                avg_values = df.iloc[:, :-1].mean()
                plt.figure(figsize=(10, 5))
                avg_values.plot(kind='bar')
                plt.xticks(range(len(avg_values.index)), range(1, len(avg_values.index) + 1))  # Set x-axis ticks to column indices
                plt.xlabel('Frequency [Hz]')
                plt.ylabel('Average Value')
                plt.title('Average Frequency Spectrum')
                st.pyplot(plt)
        else:
            st.write("No CSV files found in the 'training_data' folder.")

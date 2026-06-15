# Gambit — Brain-Controlled Pong via EEG & SSVEP

Gambit is a senior capstone project that uses EEG signals and **Steady-State Visually Evoked Potentials (SSVEP)** to control a Pong-style video game with your brain. Players focus on flickering circles at distinct frequencies (9, 12, or 15 Hz), which generate unique EEG patterns that a trained ML model classifies into game commands in real time.

> **Award:** This project won 3rd place at the IEEE Canadian Atlantic Section capstone competition.

[![Gambit Demo](https://drive.google.com/thumbnail?id=1B0RK4MlQjl3-Ow80WcBopgXp9DgFGuqh&sz=w1280)](https://drive.google.com/file/d/1B0RK4MlQjl3-Ow80WcBopgXp9DgFGuqh/view?usp=sharing)

**[Watch the Demo](https://drive.google.com/file/d/1B0RK4MlQjl3-Ow80WcBopgXp9DgFGuqh/view?usp=sharing)**

---

## How It Works

1. **Data Collection** — An EEG headset streams 34-channel frequency data over LSL. The player focuses on a circle flickering at a target frequency while data is recorded.
2. **Model Training** — Recorded data is used to train classical ML models or a 1D CNN to classify the three target frequencies.
3. **Real-Time Prediction** — During gameplay, EEG data is read from the live LSL stream, predictions are smoothed via majority voting, and the result controls the paddle position.
4. **Game** — A fullscreen Pygame Pong game where the EEG-controlled paddle moves to one of three vertical positions (top/middle/bottom) based on predicted frequency.

---

## Signal Processing Pipeline

Understanding how raw EEG signals become game commands:

### 1. Electrode Placement — Occipital Region
EEG electrodes are concentrated at the **back of the head (occipital lobe)**, which is the brain's primary visual processing center. When the eyes are exposed to a flickering stimulus, the occipital region produces the strongest and most consistent SSVEP response, making it the optimal placement for frequency-based visual BCI systems.

### 2. Channel Aggregation
The Cyton board captures multiple EEG channels simultaneously. Rather than treating each channel independently, the signals are **summed across channels** to produce a stronger composite signal. This improves the signal-to-noise ratio by reinforcing the shared SSVEP response while partially cancelling out uncorrelated noise.

### 3. Fast Fourier Transform (FFT)
The aggregated time-domain signal is converted to the **frequency domain via FFT**. This reveals the power at each frequency — when a user focuses on a 12 Hz flickering circle, a clear spike appears at 12 Hz (and often its harmonics) in the FFT output. The FFT feature vector is what gets fed into the classifier.

### 4. Classification
The FFT output is passed to a trained ML model (e.g. KNN, SVM, or CNN) which predicts which of the three target frequencies (9, 12, or 15 Hz) is dominant — corresponding to where the user is directing their attention.

### 5. Prediction Smoothing — Moving Average / Majority Vote
Raw per-frame predictions are noisy, especially during transitions when a user shifts their gaze from one stimulus to another. To handle this, predictions are smoothed using a **majority vote over a rolling buffer of 80 samples**. This acts as a low-pass filter on the prediction stream:

- **More smoothing (larger buffer)** → more stable, fewer mispredictions, but higher latency before a new intention is registered
- **Less smoothing (smaller buffer)** → faster response to intention changes, but more jitter and mispredictions during transitions between targets

The 80-sample buffer was chosen to balance responsiveness with stability for real-time gameplay.


---

## File Overview

| File | Description |
|---|---|
| `ui.py` | **Entry point.** Streamlit dashboard for data collection, model training, game launch, and data visualization. |
| `game_data_recorder.py` | Records EEG data from an LSL stream while displaying a flickering circle at the target frequency. Saves CSVs to `training_data/`. |
| `train_sklearn_models.py` | Trains 8 scikit-learn classifiers (Logistic Regression, KNN, Naive Bayes, Decision Tree, SVM, MLP, Random Forest, Gradient Boosting) on the collected data. Saves `.pkl` models to `models/`. |
| `train_cnn.py` | Trains a 1D convolutional neural network using TensorFlow. Saves a `.keras` model to `models/`. |
| `predictor_queue.py` | Loads a trained model, reads the live EEG stream, applies prediction smoothing (80-sample majority-vote buffer), and pushes commands to the game via a multiprocessing queue. |
| `gambit_game.py` | Pygame game loop. Renders the Pong game with three flickering stimulus circles. Receives paddle commands from the prediction queue. |
| `accuracies.json` | Stored model test accuracies from the most recent training run. |

### Directories

| Directory | Description |
|---|---|
| `training_data/` | CSV files of recorded EEG sessions, named `{subject}_{frequency}hz.csv`. |
| `models/` | Serialized trained models (`.pkl` and `.keras`). |
| `sound/` | Audio notification files used during data collection. |

---

## Setup

### Prerequisites

- Python 3.8+
- EEG headset with LSL support — this project uses the [OpenBCI Cyton Board](https://shop.openbci.com/products/cyton-biosensing-board-8-channel)
- LSL stream active before recording or playing

### Install Dependencies

```bash
pip install streamlit scikit-learn tensorflow pandas numpy pygame pylsl joblib
```

---

## Usage

### 1. Launch the Dashboard

```bash
streamlit run ui.py
```

### 2. Collect Training Data

- Go to the **Data Collection** tab
- Set the target frequency (9, 12, or 15 Hz) and duration (25+ seconds recommended)
- Click **Record Data** — the flickering stimulus will display; focus on it during recording
- Repeat for each frequency (multiple sessions per frequency improves accuracy)

### 3. Train Models

- Go to the **Model Training** tab
- Click **Train Models**
- A table of test accuracies for all models will appear

### 4. Play the Game

- Go to the **Game Launcher** tab
- Select a trained model from the dropdown
- Set game duration and click **Start the Game**
- Focus on the circle at the position you want the paddle to move to:
  - **9 Hz** → bottom
  - **12 Hz** → middle
  - **15 Hz** → top

### 5. Visualize Data (Optional)

- Go to the **Visualization** tab
- Select a CSV from `training_data/` to plot its frequency spectrum

---

## Model Performance

Results from training on collected data:

| Model | Test Accuracy |
|---|---|
| KNeighbors | 99.73% |
| MLP | 98.90% |
| RandomForest | 98.55% |
| SVM | 98.12% |
| GradientBoosting | 96.33% |
| DecisionTree | 94.66% |
| LogisticRegression | 91.18% |
| GaussianNB | 63.12% |

---

## Team

- Nick Rockwell
- Ahmed Khairallah
- Anirudh Nair

**External Supervisor:** Hamidreza Maymandi  
**Internal Supervisor:** Jose Gonzales-Cueto

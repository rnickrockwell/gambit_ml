import time
from pylsl import StreamInlet, resolve_stream
from time import sleep
import numpy as np
import multiprocessing
import pygame
import joblib
import pandas as pd
from gambit_game import pygame_loop
from collections import deque
from collections import defaultdict
from tensorflow import keras
import logging
from pathlib import Path
import sys

def main():
    # Timing
    model_name = Path(f"{sys.argv[1]}")
    duration = int(sys.argv[2])
    is_tf_model = False
    model_folder = Path("models")
    if model_name.suffix == '.keras':
        is_tf_model = True

    match is_tf_model:
        case True: model = keras.models.load_model(model_folder / model_name)
        case False: model = joblib.load(model_folder / model_name)
    
    smooth_model = SmoothPredict(model, is_tf_model)
    
    # Create a new inlet to read from the stream
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])

    # sound
    pygame.mixer.init()
    sound = pygame.mixer.Sound('sound/notif.mp3')
    
    # Queue for communication
    queue = multiprocessing.Queue()

    # Start the Pygame process
    pygame_process = multiprocessing.Process(target=pygame_loop, args=(queue,))
    pygame_process.start()

    # Wait for pygame
    sleep(7)

    # Some stats
    start = time.time()

    # record data
    sound.play()
   
    while time.time() <= start + duration:
        # get chunks of samples
        chunk, timestamp = inlet.pull_chunk()
        if chunk:
            avg_sample = np.zeros((1, len(chunk[0])))
            for sample in chunk:
                avg_sample += np.array(sample)

            avg_sample /= len(chunk)
            avg_sample = avg_sample[:, 1:35]
            avg_sample = np.reshape(avg_sample, (1, -1))
            prediction = smooth_model.predict(avg_sample) #model.predict(avg_sample)

            # Send prediction to the Pygame process
            queue.put(prediction)

    # Indicate the end of predictions
    queue.put('DONE')

    # Done
    sound.play()
    
    # Wait for the Pygame process to finish
    pygame_process.join()


class SmoothPredict:
    def __init__(self, model, is_tf_model):
        self.model = model
        self.buffer = deque([])
        self.counts = defaultdict(lambda: 0)
        self.size = 80
        self.mapping = [9, 12, 15]
        self.is_tf_model = is_tf_model

    def predict(self, sample):
        match self.is_tf_model:
            case True: prediction = self.mapping[np.argmax(self.model.predict(sample, verbose=0)[0])]
            case False: prediction = self.model.predict(sample)[0]

        self.buffer.append(prediction)
        self.counts[prediction] += 1

        if len(self.buffer) < self.size:
            return 12

        popped = self.buffer.popleft()
        self.counts[popped] -= 1

        return max(self.counts, key=self.counts.get)


if __name__ == '__main__':
    main()

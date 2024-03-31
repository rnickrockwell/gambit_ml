import time
from pylsl import StreamInlet, resolve_stream
from time import sleep
import numpy as np
import multiprocessing
import pygame
from gambit_game import pygame_loop
from multiprocessing import Queue
from pathlib import Path
from datetime import datetime  # Import datetime to format the file name
import sys

def main():
    # data
    args = sys.argv
    target = int(args[1])

    # Timing
    duration = int(args[2])

    # file
    data_folder = Path("training_data")  # Change to "training_data"
    data_folder.mkdir(exist_ok=True)  # Ensure the folder exists

    # Naming the file with target frequency and current date-time
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Get current date-time
    save_file_name = f"{target}hz-{current_time}.csv"  # Format the file name
    save_file = data_folder / save_file_name  # Create the full path for the file

    
    # Create a new inlet to read from the stream
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])

    # sound
    pygame.mixer.init()
    sound = pygame.mixer.Sound('sound/notif.mp3')
    
    # Launch the flasher
    queue = Queue()
    flasher_process = multiprocessing.Process(target=pygame_loop, args=(queue,))
    flasher_process.start()
    sleep(7)

    # Some stats
    start = time.time()

    # record data
    sound.play()
    with open(save_file, "w") as f:
        while time.time() <= start + duration:
            # get chunks of samples
            chunk, timestamp = inlet.pull_chunk()
            if chunk:
                avg_sample = np.zeros((1, len(chunk[0])))
                for sample in chunk:
                    avg_sample += np.array(sample)

                avg_sample /= len(chunk)
                avg_sample = avg_sample[:, 1:35]
                avg_sample = np.append(avg_sample, int(target))
                avg_sample = np.reshape(avg_sample, (1, -1))
                np.savetxt(f, avg_sample, delimiter=",", fmt="%f")
    sound.play()

    sleep(1)

    # Join the flasher process
    queue.put("DONE")
    flasher_process.join()

if __name__ == '__main__':
    main()

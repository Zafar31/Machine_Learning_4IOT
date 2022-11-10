"""
c. Modify the script to store the audio data on disk every second. 
Use the stream callback function to store data in parallel with recording. 
Use the scipy.io.wavfile.write function to store the audio data on disk. 
Use the timestamp of the recording as the filename.
"""


import os
import sounddevice as sd
import numpy as np
from time import time
from scipy.io.wavfile import write
import argparse as ap
import tensorflow as tf
import tensorflow_io as tfio


parser = ap.ArgumentParser()

parser.add_argument('--resolution', default=16000, type=int, help="Resolution for capturing audio")
# blocksize
parser.add_argument('--blocksize', default=48000, type=int, help="Blocksize for capturing audio")
parser.add_argument('--device', default=0, type=int, help="Default device is 0, change for others")


args = parser.parse_args()


def get_audio_from_numpy(indata):
    indata = tf.convert_to_tensor(indata, dtype=tf.float32)
    indata = (indata + 32768) / (32767 + 32768)
    indata = tf.squeeze(indata)
    return indata

def get_spectrogram(indata, downsampling_rate, frame_length_in_s, frame_step_in_s):
    # TODO: Write your code here
    data = get_audio_from_numpy(indata)
    

    sampling_rate_float32 = tf.cast(downsampling_rate, tf.float32)
    frame_length = int(frame_length_in_s * sampling_rate_float32)
    frame_step = int(frame_step_in_s * sampling_rate_float32)

    stft = tf.signal.stft(
        data,
        frame_length=frame_length,
        frame_step=frame_step,
        fft_length=frame_length
    )
    spectrogram = tf.abs(stft)

    return spectrogram

def is_silence(indata, downsampling_rate=16000, frame_length_in_s=0.0005, dbFSthresh=-135, duration_time=0.1):
    #audio, sampling_rate, label = get_audio_and_label(filename)

    spectrogram = get_spectrogram(
        indata,
        downsampling_rate,
        frame_length_in_s,
        frame_length_in_s
    )
    dbFS = 20 * tf.math.log(spectrogram + 1.e-6)
    energy = tf.math.reduce_mean(dbFS, axis=1)
    non_silence = energy > dbFSthresh
    non_silence_frames = tf.math.reduce_sum(tf.cast(non_silence, tf.float32))
    non_silence_duration = (non_silence_frames + 1) * frame_length_in_s

    if non_silence_duration > duration_time:
        return 0
    else:
        return 1

values = sd.query_devices()
device = 0

for value in values:
    if value['name'] == 'default':
        device = value['index']

"""
samplerate (float, optional) – 
The desired sampling frequency (for both input and output). The default value can be changed with default.samplerate.
blocksize (int, optional) – 
The number of frames passed to the stream callback function, or the preferred block granularity for a blocking read/write stream. 
The special value blocksize=0 (which is the default) may be used to request that the stream callback will receive an optimal (and possibly varying) 
number of frames based on host requirements and the requested latency settings. The default value can be changed with default.blocksize.
"""

def callback(indata, frames, callback_time, status):
    """This is called (from a separate thread) for each audio block."""
    timestamp = time()
    # print(type(indata))  # Type is numpy.ndarray
    if is_silence(indata) != '0' :
        print("Noise!")
        write(f'./AudioFiles/{timestamp}.wav', args.resolution, indata)
        filesize_in_bytes = os.path.getsize(f'./AudioFiles/{timestamp}.wav')
        filesize_in_kb = filesize_in_bytes / 1024
        print(f'Size: {filesize_in_kb:.2f}KB')

    if is_silence(indata) == '1':
        print("Silence!")

with sd.InputStream(device=device, channels=1, dtype='int16', samplerate=args.resolution, blocksize=args.blocksize, callback=callback):
    while True:
        key = input()
        if key in ('q', 'Q'):
            print('Stop recording.')
            break
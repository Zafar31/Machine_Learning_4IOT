import os
import sounddevice as sd
import numpy as np
from time import time
from scipy.io.wavfile import write
import argparse as ap
import pandas as pd
from glob import glob



def import_tensorflow():
    # Filter tensorflow version warnings
    import os
    # https://stackoverflow.com/questions/40426502/is-there-a-way-to-suppress-the-messages-tensorflow-prints/40426709
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
    import warnings
   
    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=Warning)
    import tensorflow as tf
    tf.get_logger().setLevel('INFO')
    tf.autograph.set_verbosity(0)
    import logging
    tf.get_logger().setLevel(logging.ERROR)
    return tf

tf = import_tensorflow()    
import tensorflow_io as tfio

parser = ap.ArgumentParser()

parser.add_argument('--resolution', default=16000, type=int, help="Resolution for capturing audio")
# blocksize
parser.add_argument('--blocksize', default=48000, type=int, help="Blocksize for capturing audio")
parser.add_argument('--device', default=0, type=int, help="Default device is 0, change for others")


args = parser.parse_args()


def get_audio_from_numpy(indata):
    #added
    audio_binary = tf.io.read_file(filename)
    audio, sampling_rate = tf.audio.decode_wav(audio_binary)
    
    #

    indata = tf.convert_to_tensor(audio, dtype=tf.float32)
    indata = (indata + 32768) / (32767 + 32768)
    indata = tf.squeeze(indata)
    return indata


def get_audio_and_label(filename):
    # TODO: Write your code here
    audio_binary = tf.io.read_file(filename)
    audio, sampling_rate = tf.audio.decode_wav(audio_binary)
    
    audio = tf.squeeze(audio)

    zero_padding = tf.zeros(sampling_rate - tf.shape(audio), dtype=tf.float32)
    audio_padded = tf.concat([audio, zero_padding], axis=0)

    return audio

def get_spectrogram(indata, downsampling_rate, frame_length_in_s, frame_step_in_s):
    # TODO: Write your code here
    # data = get_audio_and_label(indata)
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

print("################################################")
for filename in glob('./AudioFiles/*'):
    print(filename)
    print(is_silence(filename))
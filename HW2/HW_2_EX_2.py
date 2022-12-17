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
parser.add_argument('--blocksize', default=16000, type=int, help="Blocksize for capturing audio")
parser.add_argument('--device', default=0, type=int, help="Default device is 0, change for others")
parser.add_argument('--output_directory', default='./AudioFiles',type=str, help='Used to specify output folder')

args = parser.parse_args()


#used for the model
LABELS = ['down', 'go', 'left', 'no', 'right', 'stop', 'up', 'yes']
MODEL_NAME = "model13"
interpreter = tf.lite.Interpreter(model_path=f'./tflite_models/{MODEL_NAME}.tflite')
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
# end of model



def get_audio_from_numpy(indata):
    indata = tf.convert_to_tensor(indata, dtype=tf.float32)
    indata = 2* ((indata + 32768) / (32767 + 32768)) -1
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

linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
    num_mel_bins=25,
    num_spectrogram_bins=321,
    sample_rate=16000,
    lower_edge_hertz=20,
    upper_edge_hertz=4000
)
state = False

def calculate_next_state_FSM(indata):
    print("Test")
    frame_length = 0.04
    frame_step   = 0.04
    status = state
    ###
    data = get_audio_from_numpy(indata)
    # audio_binary = tf.io.read_file(filename)
    audio, sampling_rate = tf.audio.decode_wav(data)
    audio = tf.squeeze(audio)
    zero_padding = tf.zeros(sampling_rate - tf.shape(audio), dtype=tf.float32)
    audio_padded = tf.concat([audio, zero_padding], axis=0)

    stft = tf.signal.stft(
        audio_padded,
        frame_length=frame_length,
        frame_step=frame_step,
        fft_length=frame_length
    )
    spectrogram = tf.abs(stft)
    mel_spectrogram = tf.matmul(spectrogram, linear_to_mel_weight_matrix)
    log_mel_spectrogram = tf.math.log(mel_spectrogram + 1.e-6)
    log_mel_spectrogram = tf.expand_dims(log_mel_spectrogram, 0)  # batch axis
    log_mel_spectrogram = tf.expand_dims(log_mel_spectrogram, -1)  # channel axis
    mfcss = tf.signal.mfccs_from_log_mel_spectrograms(log_mel_spectrogram)
    interpreter.set_tensor(input_details[0]['index'], mfcss)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    # top_index = np.argmax(output[0])
    # predicted_label = LABELS[top_index]
    ###
    if (output[0][5] > threshold):
        print("Start monitoring")
        status = True
    if (output[0][1] > threshold):
        print("Stop monitoring")
        status = False

    return state



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
    # print(is_silence(indata))
    # print(type(indata))  # Type is numpy.ndarray
    if is_silence(indata) == 0 :
        print("Noise!")

        #calculate next step of FSM!
        state = calculate_next_state_FSM(indata)
        #

        write(f'{args.output_directory}/{timestamp}.wav', args.resolution, indata)
        filesize_in_bytes = os.path.getsize(f'./AudioFiles/{timestamp}.wav')
        filesize_in_kb = filesize_in_bytes / 1024
        print(f'Size: {filesize_in_kb:.2f}KB')

    else:
        print("Silence!")

def main():
    # with sd.InputStream(device=args.device, channels=1, dtype='int16', samplerate=args.resolution, blocksize=args.blocksize, callback=callback):
    #     while True:
    #         key = input()
    #         if key in ('q', 'Q'):
    #             print('Stop recording.')
    #             break

    # Update the battery monitoring script of LAB1 – Exercise 2 integrating a Voice User Interface (VUI)
    # based on VAD and KWS.

    # The monitoring system must measure the battery status (battery level and power plugged) every 1
    # second and store the collected data on Redis (follow the specifications of LAB1 – Exercise 2c for the
    # timeseries naming).
    mac_address = hex(uuid.getnode())
    redis_client = redis.Redis(host=redis_host, port=redis_port, username=REDIS_USERNAME, password=REDIS_PASSWORD)
    
    bucket_1d_in_ms=86400000
    one_mb_time_in_ms = 655359000
    five_mb_time_in_ms = 3276799000

    try:
        redis_client.ts().create('{mac_address}:battery', chunk_size=4, retention=five_mb_time_in_ms)
        redis_client.ts().create('{mac_address}:power', chunk_size=4, retention=five_mb_time_in_ms)
    except redis.ResponseError:
        print("Cannot create some TimeSeries")
        pass
    
    while True:
        print("Start")
        if(state == False):
            print("System is not monitoring")

        if(state == True):
            print("System is monitoring")
        
        #check if silence
        with sd.InputStream(device=args.device, channels=1, dtype='int16', samplerate=args.resolution, blocksize=args.blocksize, callback=callback):
            print("Check Silence")

    # The VUI must provide the user the possibility to start/stop the battery monitoring using “go/stop”
    # voice commands.
    # Specifically, the script must implement the following behavior:

    # • Initially, the monitoring is disabled.

    # • The VUI always runs in background and continuously records audio data with your PC and
    # the integrated/USB microphone. Every 1 second, the VUI checks if the recording contains
    # speech using the VAD function developed in LAB2 – Exercise 2 (or its optimized version
    # developed in Homework 1).

    # • If the VAD returns no silence, the recording is fed to the classification model for “go/stop”
    # spotting developed in 1.1 and one of the following actions is performed:
    # o If the predicted keyword is “go” with probability > 95%, start the monitoring.
    # o If the predicted keyword is “stop” with probability > 95%, stop the monitoring.
    # o If the top-1 probability (regardless of the predicted label) is ≤ 95%, remain in the
    # current state.
    # • If the VAD returns silence, remain in the current state.
    # The script should be run from the command line interface and should take as input the following
    # arguments:
    # • --device (int): the ID of the microphone used for recording.
    # • --host (str): the Redis Cloud host.
    # • --port (int): the Redis Cloud port.
    # • --user (str): the Redis Cloud username.
    # • --password (str): the Redis Cloud

if __name__ == '__main__':
    output_directory = args.output_directory

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    main()

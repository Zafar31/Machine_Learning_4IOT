import os
import sounddevice as sd
import numpy as np
import time
from time import time
from time import sleep
from scipy.io.wavfile import write
import argparse as ap
import tensorflow as tf
import tensorflow_io as tfio
import uuid
import redis
import psutil
# import myConnection as mc


from datetime import datetime
import argparse as ap


parser = ap.ArgumentParser()

parser.add_argument('--resolution', default=16000, type=int, help="Resolution for capturing audio")
# blocksize
parser.add_argument('--blocksize', default=16000, type=int, help="Blocksize for capturing audio")
parser.add_argument('--device', default=0, type=int, help="Default device is 0, change for others")
#redis args
parser.add_argument('--host', default='redis-13196.c293.eu-central-1-1.ec2.cloud.redislabs.com', type=str, help="Default host change for others")
parser.add_argument('--port', default=13196, type=int, help="Default port change for others")
parser.add_argument('--user', default='default', type=str, help="Default user change for others")
parser.add_argument('--password', default='NGbg7uGecevRJY9qTEutCrumkPOMwj4J', type=str, help="Default password change for others")
parser.add_argument('--flushDB', default=0, type=int, help="Set 1 to flush all database. Default is 0")

args = parser.parse_args()

LABELS = ['down', 'go', 'left', 'no', 'right', 'stop', 'up', 'yes']
MODEL_NAME = "model13"
interpreter = tf.lite.Interpreter(model_path=f'./{MODEL_NAME}.tflite')
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def get_audio_from_numpy(indata):
    indata = tf.convert_to_tensor(indata, dtype=tf.float32)
    indata = 2* ((indata + 32768) / (32767 + 32768)) -1
    indata = tf.squeeze(indata)
    return indata

def get_spectrogram(indata, downsampling_rate, frame_length_in_s, frame_step_in_s):
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
    num_mel_bins=31,
    num_spectrogram_bins=257,
    sample_rate=16000,
    lower_edge_hertz=80,
    upper_edge_hertz=8000
)

state = False

def calculate_next_state_FSM(indata):
    frame_length_in_s = 0.032
    frame_step_in_s   = 0.032
    global state
    data = get_audio_from_numpy(indata)
    audio=data
    zero_padding = tf.zeros(16000 - tf.shape(audio), dtype=tf.float32)
    audio_padded = tf.concat([audio, zero_padding], axis=0)
    frame_length = int(frame_length_in_s * 16000)
    frame_step = int(frame_step_in_s * 16000)
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

    threshold = 0.95
    print("Stop:",output[0][5]*100,"%")
    print("Go",output[0][1]*100,"%")
    if (output[0][1] > threshold):
        print("Start monitoring")
        state = True
    if (output[0][5] > threshold):
        print("Stop monitoring")
        state = False
    return state



values = sd.query_devices()
device = 0

for value in values:
    if value['name'] == 'default':
        device = value['index']

# Connect to Redis
# redis_host, redis_port, REDIS_USERNAME, REDIS_PASSWORD = mc.getMyConnectionDetails()

redis_host     = args.host
redis_port     = args.port
REDIS_USERNAME = args.user
REDIS_PASSWORD = args.password

redis_client = redis.Redis(host=redis_host, port=redis_port, username=REDIS_USERNAME, password=REDIS_PASSWORD)
is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

mac_address = hex(uuid.getnode())

bucket_1d_in_ms=86400000
one_mb_time_in_ms = 655359000
five_mb_time_in_ms = 3276799000

if args.flushDB:
    try:
        redis_client.flushall()
    except redis.ResponseError:
        print("Cannot flush")
        pass
try:
    redis_client.ts().create('{mac_address}:battery', chunk_size=128, retention=five_mb_time_in_ms)
    redis_client.ts().create('{mac_address}:power', chunk_size=128, retention=five_mb_time_in_ms)
except redis.ResponseError:
    print("Cannot create some TimeSeries, maybe they already exist")
    pass

def callback(indata, frames, callback_time, status):
    timestamp = time()
    global state
    global mac_address
    if is_silence(indata) == 0 :
        #calculate next step of FSM!
        state = calculate_next_state_FSM(indata)

    if(state == False):
        print("System is not monitoring")

    if(state == True):
        print("System is monitoring")
        timestamp_ms = int(time() * 1000)
        battery_level = psutil.sensors_battery().percent
        power_plugged = int(psutil.sensors_battery().power_plugged)
        redis_client.ts().add('{mac_address}:battery', timestamp_ms, battery_level)
        redis_client.ts().add('{mac_address}:power', timestamp_ms, power_plugged)
        formatted_datetime = datetime.fromtimestamp(time() ).strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'{formatted_datetime} - {mac_address}:battery = {battery_level}')
        print(f'{formatted_datetime} - {mac_address}:power = {power_plugged}')

def main():

    while True:
        with sd.InputStream(device=args.device, channels=1, dtype='int16', samplerate=args.resolution, blocksize=args.blocksize, callback=callback):
            print("") # to print a new line, improving readability in the terminal

if __name__ == '__main__':
    main()

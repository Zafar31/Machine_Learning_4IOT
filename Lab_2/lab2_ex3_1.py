"""
This example shows how to enable/disable lossless compression in Redis TimeSeries.
Moreover, it shows how to retrieve the memory usage and the # records of a TimeSeries.
"""
import redis

import psutil
import uuid
import time
from time import sleep
from time import time
from datetime import datetime


mac_address = hex(uuid.getnode())

# Connect to Redis
redis_host = "******"
redis_port = **************
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'your-password'


redis_client = redis.Redis(host=redis_host, port=redis_port)
is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

retention_period_1d=86400000
retention_period_30d=retention_period_1d*30



# Create a TimeSeries with chunk size 128 bytes
# By default, compression is enabled
try:
    redis_client.ts().create('0xb0a46095b5ff:battery', chunk_size=128, retention=retention_period_1d)
    redis_client.ts().create('0xb0a46095b5ff:power', chunk_size=128, retention=retention_period_1d)
    redis_client.ts().create('0xb0a46095b5ff:battery_min', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('0xb0a46095b5ff:battery','0xb0a46095b5ff:battery_min',min,60000)
    redis_client.ts().create('0xb0a46095b5ff:battery_max', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('0xb0a46095b5ff:battery','0xb0a46095b5ff:battery_max',max,60000)
    redis_client.ts().create('0xb0a46095b5ff:battery_avg', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('0xb0a46095b5ff:battery','0xb0a46095b5ff:battery_avg',avg,30000)
    redis_client.ts().create('0xb0a46095b5ff:power_avg', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('0xb0a46095b5ff:power','0xb0a46095b5ff:power_avg',avg,30000)
    redis_client.ts().create('0xb0a46095b5ff:battery_uncompressed', chunk_size=128, retention=retention_period_1d)
    redis_client.ts().create('0xb0a46095b5ff:power_uncompressed', chunk_size=128, retention=retention_period_1d)
    redis_client.ts().create('0xb0a46095b5ff:battery_min_uncompressed', chunk_size=128, retention=retention_period_30d)

    redis_client.ts().createrule('0xb0a46095b5ff:battery_uncompressed','0xb0a46095b5ff:battery_min_uncompressed',min,60000)
    redis_client.ts().create('0xb0a46095b5ff:battery_max_uncompressed', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('0xb0a46095b5ff:battery_uncompressed','0xb0a46095b5ff:battery_max_uncompressed',max,60000)
    redis_client.ts().create('0xb0a46095b5ff:battery_avg_uncompressed', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('0xb0a46095b5ff:battery_uncompressed','0xb0a46095b5ff:battery_avg_uncompressed',avg,30000)
    redis_client.ts().create('0xb0a46095b5ff:power_avg_uncompressed', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('0xb0a46095b5ff:power_uncompressed','0xb0a46095b5ff:power_avg_uncompressed',avg,30000)
    # redis_client.ts().create('temperature', chunk_size=128)
except redis.ResponseError:
    print("Cannot create some TimeSeries")
    pass


######################################################
wait_15_minutes=60*15

print("START")

while True:
    timestamp_ms = int(time() * 1000)
    battery_level = psutil.sensors_battery().percent
    power_plugged = int(psutil.sensors_battery().power_plugged)
    redis_client.ts().add('0xb0a46095b5ff:battery', timestamp_ms, battery_level)
    redis_client.ts().add('0xb0a46095b5ff:power', timestamp_ms, power_plugged)
    redis_client.ts().add('0xb0a46095b5ff:battery_uncompressed', timestamp_ms, battery_level)
    redis_client.ts().add('0xb0a46095b5ff:power_uncompressed', timestamp_ms, power_plugged)

    formatted_datetime = datetime.fromtimestamp(time() ).strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f'{formatted_datetime} - {mac_address}:battery = {battery_level}')
    print(f'{formatted_datetime} - {mac_address}:power = {power_plugged}')

    sleep(1)


    # timestamp = time.time()
    # battery_level = psutil.sensors_battery().percent
    # power_plugged = int(psutil.sensors_battery().power_plugged)
    # formatted_datetime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

    # print(f'{formatted_datetime} - {mac_address}:battery = {battery_level}')
    # print(f'{formatted_datetime} - {mac_address}:power = {power_plugged}')
    # time.sleep(5)

######################################################




# print('===temperature info===')
# print('Memory Usage (bytes):', redis_client.ts().info('temperature').memory_usage)
# print('Total Samples:', redis_client.ts().info('temperature').total_samples)
# print('# of Chunks:',  redis_client.ts().info('temperature').chunk_count)
# print()

# print('Adding 100 values to "temperature"')
# print()
# for i in range(100):
#     timestamp_ms = int(time() * 1000)
#     redis_client.ts().add('temperature', timestamp_ms, 25 + i // 50)
#     sleep(0.1)

# print('===temperature info===')
# print('Memory Usage (bytes):', redis_client.ts().info('temperature').memory_usage)
# print('Total Samples:', redis_client.ts().info('temperature').total_samples)
# print('# of Chunks:',  redis_client.ts().info('temperature').chunk_count)
# print()

# # Disable compression
# try:
#     redis_client.ts().create('temperature_uncompressed', chunk_size=128, uncompressed=True)
# except redis.ResponseError:
#     pass

# print('Adding 100 values to "temperature_uncompressed"')
# for i in range(100):
#     timestamp_ms = int(time() * 1000)
#     redis_client.ts().add('temperature_uncompressed', timestamp_ms, 25 + i // 50)
#     sleep(0.1)

# print('===temperature_uncompressed info===')
# print('Memory Usage (bytes):', redis_client.ts().info('temperature_uncompressed').memory_usage)
# print('Total Samples:', redis_client.ts().info('temperature_uncompressed').total_samples)
# print('# of Chunks:',  redis_client.ts().info('temperature_uncompressed').chunk_count )
# print()

# compressed_memory = redis_client.ts().info('temperature').memory_usage
# uncompressed_memory = redis_client.ts().info('temperature_uncompressed').memory_usage
# savings = 100 * (uncompressed_memory - compressed_memory) / uncompressed_memory
# print(f'Memory Savings: {savings:.2f}%')

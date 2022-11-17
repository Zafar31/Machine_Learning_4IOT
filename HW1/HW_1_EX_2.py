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
    redis_client.ts().create('{mac_address}:battery', chunk_size=128, retention=retention_period_1d)
    redis_client.ts().create('{mac_address}:power', chunk_size=128, retention=retention_period_1d)
    redis_client.ts().create('{mac_address}:battery_min', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('{mac_address}:battery','{mac_address}:battery_min',min,60000)
    redis_client.ts().create('{mac_address}:battery_max', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('{mac_address}:battery','{mac_address}:battery_max',max,60000)
    redis_client.ts().create('{mac_address}:battery_avg', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('{mac_address}:battery','{mac_address}:battery_avg',avg,30000)
    redis_client.ts().create('{mac_address}:power_avg', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('{mac_address}:power','{mac_address}:power_avg',avg,30000)
    redis_client.ts().create('{mac_address}:battery_uncompressed', chunk_size=128, retention=retention_period_1d)
    redis_client.ts().create('{mac_address}:power_uncompressed', chunk_size=128, retention=retention_period_1d)
    redis_client.ts().create('{mac_address}:battery_min_uncompressed', chunk_size=128, retention=retention_period_30d)

    redis_client.ts().createrule('{mac_address}:battery_uncompressed','{mac_address}:battery_min_uncompressed',min,60000)
    redis_client.ts().create('{mac_address}:battery_max_uncompressed', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('{mac_address}:battery_uncompressed','{mac_address}:battery_max_uncompressed',max,60000)
    redis_client.ts().create('{mac_address}:battery_avg_uncompressed', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('{mac_address}:battery_uncompressed','{mac_address}:battery_avg_uncompressed',avg,30000)
    redis_client.ts().create('{mac_address}:power_avg_uncompressed', chunk_size=128, retention=retention_period_30d)
    redis_client.ts().createrule('{mac_address}:power_uncompressed','{mac_address}:power_avg_uncompressed',avg,30000)
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
    redis_client.ts().add('{mac_address}:battery', timestamp_ms, battery_level)
    redis_client.ts().add('{mac_address}:power', timestamp_ms, power_plugged)
    redis_client.ts().add('{mac_address}:battery_uncompressed', timestamp_ms, battery_level)
    redis_client.ts().add('{mac_address}:power_uncompressed', timestamp_ms, power_plugged)

    formatted_datetime = datetime.fromtimestamp(time() ).strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f'{formatted_datetime} - {mac_address}:battery = {battery_level}')
    print(f'{formatted_datetime} - {mac_address}:power = {power_plugged}')

    sleep(1)

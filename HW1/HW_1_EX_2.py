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
import myConnection as mc



mac_address = hex(uuid.getnode())

# Connect to Redis
redis_host, redis_port, REDIS_USERNAME, REDIS_PASSWORD = mc.getMyConnectionDetails()


redis_client = redis.Redis(host=redis_host, port=redis_port, username=REDIS_USERNAME, password=REDIS_PASSWORD)
is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

bucket_1d_in_ms=86400000
one_mb_time_in_ms = 655359000
five_mb_time_in_ms = 3276799000


# Create a TimeSeries with chunk size 128 bytes
# By default, compression is enabled
try:
    redis_client.flushall()
except redis.ResponseError:
    print("Cannot flush")
    pass
try:
    redis_client.ts().create('{mac_address}:battery', chunk_size=128, retention=five_mb_time_in_ms)
    redis_client.ts().create('{mac_address}:power', chunk_size=128, retention=five_mb_time_in_ms)
    redis_client.ts().create('{mac_address}:plugged_seconds', chunk_size=128, retention=one_mb_time_in_ms)
except redis.ResponseError:
    print("Cannot create some TimeSeries")
    pass
try:
    redis_client.ts().createrule('{mac_address}:power','{mac_address}:plugged_seconds','sum',bucket_1d_in_ms)
except redis.ResponseError:
    print("Cannot create rule")
    pass

######################################################
wait_15_minutes=60*15
# timestamp_ms = int(time() * 1000)
# redis_client.ts().add('{mac_address}:plugged_seconds', timestamp_ms, 0)
    

print("START")

while True:
    timestamp_ms = int(time() * 1000)
    battery_level = psutil.sensors_battery().percent
    power_plugged = int(psutil.sensors_battery().power_plugged)
    redis_client.ts().add('{mac_address}:battery', timestamp_ms, battery_level)
    redis_client.ts().add('{mac_address}:power', timestamp_ms, power_plugged)

    formatted_datetime = datetime.fromtimestamp(time() ).strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f'{formatted_datetime} - {mac_address}:battery = {battery_level}')
    print(f'{formatted_datetime} - {mac_address}:power = {power_plugged}')

    sleep(1)

import requests
import json
import pandas as pd


host = "http://127.0.0.1:8081"

# mac  = "0x38baf8d968e9"

mac_addresses = []

# A
#get all macs
response = requests.get(host+"/devices")

# print(response.status_code)
if response.status_code == 200:
    # print(response)
    objs=response.json()['mac_addresses']
    for obj in objs:
        # print(obj)
        mac_addresses.append(obj)
    # print(obj['mac_addresses'])
    
else:
    print("The server is offline")
    exit()


# B
#get dataframe for given mac and time
# number_of_devices_monitored = len(mac_addresses)

# mac_addresses.pop()

for mac_address in mac_addresses:
    # number_of_devices_monitored -= 1
    # print(mac_address)
    request_path = host+"/device/"+ mac_address + "?fromtime=1673470855000&totime=1674248455000"
    # print(request_path)
    response = requests.get(request_path)

    # response = response.json["mac_address"] 
    # response = str(response.content)
    # response = json.loads(response)
    # response = json.dump(fp = "./test_new.json",fp = ./)
    mac_address_details_in_string = str(response.content.decode())
    # print(mac_address_details_in_string)
    # mac_address_details_in_json = json.parse(mac_address_details_in_string)
    mac_address_details_in_json = json.loads(mac_address_details_in_string)
    # print(mac_address_details_in_json.keys())

    print(mac_address_details_in_json["mac_address"])
    print(mac_address_details_in_json["timestamps"])
    print(mac_address_details_in_json["battery_levels"])
    # print(mac_address_details_in_json["power_plugged"])
    

    mac_address = mac_address_details_in_json["mac_address"]
    mac_address_x = mac_address_details_in_json["timestamps"]
    mac_address_b = mac_address_details_in_json["battery_levels"]
    mac_address_p = mac_address_details_in_json["power_plugged"]

    df_battery = pd.DataFrame([mac_address_x,mac_address_b], columns=['Datetime', 'Battery'])
    #display(df_battery)
    #import matplotlib.pyplot as plt
    df_battery.plot(x='Datetime', y='Battery')#, kind='scatter') #'Datetime', 'Battery'
    plt.show()



# if response.status_code == 200:
#     print("hello")
# else:
#     print("The server is offline")
#     exit()


# C
mac_Address_to_be_deleted = mac_addresses.pop()
print("Deleting : "+mac_Address_to_be_deleted)
#return mac_address_to_monitor
try:
    found = redis_client.delete(mac_address_to_monitor+':battery')
    found = redis_client.delete(mac_address_to_monitor+':power')
except redis.ResponseError:
    print("No keys are left for you! :)")
    pass
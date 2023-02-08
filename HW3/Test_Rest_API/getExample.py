import requests

# Thanks to guerrilla mail to providing me a chance to create an account that can get published :D
# tunzusal@sharklasers.com
# User: "Admin"  
# Password: "Testingpurposes"

print("First stage")

response = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest',
                        params={'symbol': 'BTC'},
                        headers={'X-CMC_PRO_API_KEY': '46190891-420c-44cd-9d80-789ae6cda8ed'})

response_data = response.json()
price = response_data['data']['BTC']['quote']['USD']['price']

print(f'The current price of Bitcoin is ${price:.2f}')

########## Second part
# Save to a file
print("Second stage")

import json

# convert into JSON:
y = json.dumps(response_data)

# the result is a JSON string:
print(y)

# write to file
with open("savedBTC_price_JSON.json", "w") as outfile:
    outfile.write(y)

########## Third part
# Read from a file

import json

print("Third stage")

# read from file
with open("savedBTC_price_JSON.json", "r") as infile:
    data = infile.read()

# parse file
obj = json.loads(data)

# obj is a Python object (dict):
# print(obj)
print(obj['data']['BTC']['quote']['USD']['price'])
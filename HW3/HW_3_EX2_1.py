import cherrypy
import json
import redis
import psutil
import uuid
from redis.commands.json.path import Path
import pandas as pd
import time
from datetime import datetime


REDIS_HOST = 'redis-18326.c55.eu-central-1-1.ec2.cloud.redislabs.com'
REDIS_PORT = 18326
REDIS_USERNAME = 'default'
REDIS_PASSWORD = '4BjSUT7diE4N72W5WPpJcP7hAH41IPc4'

# Connect to Redis server

redis_client = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    username=REDIS_USERNAME, 
    password=REDIS_PASSWORD)
is_connected = redis_client.ping()
print('Redis Connected:', is_connected)
redis_client.flushdb()
keys = redis_client.keys('*')
print(keys)

mac_addresses = set()
# endpoint /devices 
# GET/devices
# path parameters No
# Query parameters NO
# Response status code 200 OK
# Response schema: mac_addresses (list of string)


class Status(object):
    exposed = True

    def GET(self, *path, **query):
        global mac_addresses
        mac_addresses = set()
        keys = redis_client.keys('*')
        for key in keys:
            mac_addr = str(key).split(":")[0]
            mac_addr=mac_addr[2:]
            mac_addresses.add(mac_addr)
        response = "{mac_addresses:"
        response += str(list(mac_addresses))
        response += "}"
    
        return response



# endpoint /device/{mac_address}


# PUT/devices/{mac_address}
# Path parameters
#    mac_address(string, required)
# Query Parameters
#    from----start of the time(int,required,in ms)
#    to-------end od the time(int,required,in ms)
# Response status code:
#  200 OK
#  400 Mac address missing

#  400 start time missing
#  400 end time missing

#  404 invalid Mac address
# Response schema: 
# mac_address (string)
# timestamps(list of integer)
# battery_levels(list of integer)
# power_plugged(list of integer)

class TodoDetail(object):
    exposed = True 
    #@cherrypy.tools.json_out()
    #@cherrypy.tools.json_in()
    
    def GET(self, *path, **query):
        #fromtime = None
        #totime = None
        
        #return query.json.
        #keys = redis_client.keys('*')
           
        path = next(iter(path))
        #return path
        #if len(path) != 1:
         #   raise cherrypy.HTTPError(400, 'Bad Request: missing MAC address')
       
        #return path[1:-1]
        
        fromtime = query.get('fromtime',None)
        totime = query.get('totime',None)
        
    
        if fromtime and totime:
            mac_address_to_monitor = path
            values_battery = redis_client.ts().range('{}:battery'.format(mac_address_to_monitor), fromtime, totime)
            values_power = redis_client.ts().range('{}:power'.format(mac_address_to_monitor), fromtime, totime)
            df_battery = pd.DataFrame(values_battery, columns=['Datetime', 'Battery'])
            df_power = pd.DataFrame(values_power, columns=['Datetime', 'Power'])
            
            big_df = pd.merge(df_battery, df_power, how='inner', left_on = 'Datetime', right_on = 'Datetime')
            
            result_dict = {}
            
            result_dict["mac_address"] = mac_address_to_monitor
            result_dict["timestamps"]= list(big_df['Datetime'])
            result_dict["battery_levels"]=list(big_df["Battery"])
            result_dict["power_plugged"]=list(big_df["Power"])
            
            big_df = big_df.astype({'Battery':'int'})
            big_df = big_df.astype({'Power':'int'})
            
            result = json.dumps(result_dict)
            
            response = "{\nmac_address:"
            response += str(mac_address_to_monitor)
            response += ",\n"
            response += "timestamps:"
            response += str(list(big_df['Datetime']))
            response += ",\n"
            response += "battery_levels:"
            response += str(list(big_df["Battery"]))
            response += ",\n"
            response += "power_plugged:"
            response += str(list(big_df["Power"]))
            response += ",\n"
            response += "}"
            
            return response
            #return big_df.to_html()
        else:
            return '''
                <html>
                    <body>
                        <form method="get" action="">
                            Fromtime: <input type="text" name="fromtime" />
                            Totime: <input type="text" name="totime" />
                            <input type="submit" value="My button!" />
                        </form>
                    </body>
                </html>
            '''
            
        

        
# DELETE/devices/{mac_address}
# Path parameters
#    mac_address(string, required)
# Query Parameters NO

# Response status code:
#  200 OK
#  400 Mac address missing
#  404 invalid Mac address

# Response schema: 
    def DELETE(self, *path, **query):
        
        # path = next(iter(path))
        path = path[0]
        #return path
        # return path
       
            
        mac_address_to_monitor = str(path)
        #return mac_address_to_monitor
        try:
            found = redis_client.delete(mac_address_to_monitor+':battery')
            found = redis_client.delete(mac_address_to_monitor+':power')
        except redis.ResponseError:
            pass

        # return found

        if found == 0:
            raise cherrypy.HTTPError(404, '404 Not Found')

            # return
        else:
            return "Mac address has been deleted from redis serves"
   
    

if __name__ == '__main__':
    conf = {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}
    cherrypy.tree.mount(Status(), '/devices', conf)
    cherrypy.tree.mount(TodoDetail(), '/device', conf)
    #cherrypy.tree.mount(TodoDetail(), '/device', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start() 
    #cherrypy.quickstart()
    cherrypy.engine.block()
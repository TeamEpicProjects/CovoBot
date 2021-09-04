# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import re
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []



class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print("I am from action file")
        dispatcher.utter_message(text="Hello World response from action.py")

        return []


class Action_corona_stat(Action):

    def name(self) -> Text:
        return "action_corona_stat"
    def flatten_json(self , y):
        out = {}
        def flatten(x, name=''):
            # If the Nested key-value
            # pair is of dict type
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '_')
            elif type(x) is list:
            # If the Nested key-value
            # pair is of list type
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '_')
                    i += 1
            else:
                out[name[:-1]] = x
        flatten(y)
        return out

    def get_sats(self , name , a):
        res = ""
        for i in a.keys ():
        
            if ( len (re.findall(r"(.+?){fname}(.+?)".format(fname=name),i)) != 0 ):
                print ( "Match OFund")
                res += str(i) + " " + str(a[i]) + "\n" 
        return res.replace("_" , " " )

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        url= "https://data.covid19india.org/v4/min/data.min.json"
        r= requests.get(url = url).json()
        flattedDict = self.flatten_json(r)
        message = self.get_sats("Pathankot" , flattedDict)
        print(message)
        dispatcher.utter_message(message)
        return [] 

# class Action_corona_stat(Action):
#      def name(self) -> Text:
#          return "action_corona_stat"
#      def run(self, dispatcher: CollectingDispatcher,
#              tracker: Tracker,
#              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
#          api_res = requests.get("https://data.covid19india.org/data.json").json()

#          entities = tracker.latest_message['entities']
#          print("Last message now", entities)
#          state = None

#          for e in entities:
#              if e['entity'] == "date":
#                  date = e['value']
#          message = "Please correct State name"
#          for data in api_res["cases_time_series"]:
#              if data["date"] == date.title():
#                  print(data)
#                  message = "Active:"+ data["active"]+"\n"+ "Confirmed:"+ data["confirmed"]+"\n"+"Deaths:"+ data["deaths"]+"\n"+"Deltaconfirmed:"+ data["deltaconfirmed"]+"\n"+"Deltadeaths:"+ data["deltadeaths"]+"\n"+"Deltarecovered:"+ data["deltarecovered"]+"\n"+"Last Updated Time:"+ data["lastupdatedtime"]+"\n"+"Migrated Other:"+ data["migratedother"]+"\n"+"Recovered:"+ data["recovered"]+"\n"+"State:"+ data["state"]+"\n"+"State Code:"+ data["statecode"]+"\n"+"State Notes:"+ data["statenotes"]		
#          print(message)
#          dispatcher.utter_message(message)

#          return []         
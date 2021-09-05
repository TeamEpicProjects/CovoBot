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

    ## Custom function for json preprocessing. This will flattend the json for further steps
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

    ## This will fetch the given state or districts data provided an input
    def get_sats(self , entity_from_chatbot , flattedDict , state = False):
        res = ""
        for i in flattedDict.keys ():
            if (state == False and len (re.findall(r"(.+?){fname}(.+?)".format(fname=entity_from_chatbot),i)) != 0 ):
                res += str(i) + " " + str(flattedDict[i]) + "\n" 
            if ( state == True and len (re.findall(r"{fname}_total.+?".format(fname=entity_from_chatbot),i)) != 0):
                res += str(i) + " " + str(flattedDict[i]) + "\n" 
        
        return res.replace("_" , " " )


    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ## For better output formatting
        def get_key(val , dict_to_search_from):
            for key, value in dict_to_search_from.items():
                if val == value:
                    return key
            return "key doesn't exist" 

        ## To get the slot value from chatbot context. ie: fetching entites
        entity_from_chatbot = next(tracker.get_latest_entity_values('States'), None)
        print ("State to be processed : ", entity_from_chatbot.title() )
        
        ## API URL and the API call we need to do 
        url= "https://data.covid19india.org/v4/min/data.min.json"
        r= requests.get(url = url).json()

        ## Preprocessing of data. Flattening the dict so that it will work with regex
        flattedDict = self.flatten_json(r)

        ## Preprocessing: defining the state codes for states and UT
        st = {'Andhra Pradesh': 'AP', 'Arunachal Pradesh': 'AR', 'Assam': 'AS', 'Bihar': 'BR', 'Chhattisgarh': 'CT', 'Goa': 'GA', 'Gujarat': 'GJ', 
                'Haryana': 'HR', 'Himachal Pradesh': 'HP', 'Jharkhand': 'JH', 'Karnataka': 'KA', 'Kerala': 'KL', 'Madhya Pradesh': 'MP', 'Maharashtra': 'MH',
                'Manipur': 'MN', 'Meghalaya': 'ML', 'Mizoram': 'MZ', 'Nagaland': 'NL', 'Orissa': 'OR', 'Punjab': 'PB', 'Rajasthan': 'RJ', 'Sikkim': 'SK', 'Tamil Nadu': 'TN',
                'Telangana': 'TG', 'Tripura': 'TR', 'Uttarakhand': 'UL', 'Uttar Pradesh': 'UP', 'West Bengal': 'WB', 'Andaman and Nicobar Islands': 'AN', 'Chandigarh': 'CH',
                'Dadra and Nagar Haveli': 'DN', 'Daman and Diu': 'DD', 'Delhi': 'DL', 'Jammu and Kashmir': 'JK', 'Ladakh': 'LA', 'Lakshadweep': 'LD', 'Pondicherry': 'PY', 
                'Jammu And Kashmir': 'JK', 'Andaman And Nicobar Islands': 'AN', 'Daman And Diu': 'DD'}
        
        ## The main code that is responsible for serching through the data
        ## This if computes  if the given input is a state or not and searches accordingly
        if ( entity_from_chatbot.title() in st):
            message = self.get_sats(st[entity_from_chatbot.title().strip()] , flattedDict , True).replace( st[entity_from_chatbot.title()] , entity_from_chatbot.title() )
        else:
            message = self.get_sats(entity_from_chatbot.title().strip() , flattedDict )
            message = message.replace( message[0:2] , get_key(message[0:2] , st))

        ## giving the output to the chatbot 
        print(message)
        dispatcher.utter_message(message)
        return [] 

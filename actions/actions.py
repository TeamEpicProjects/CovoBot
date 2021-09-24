# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
import requests
import re
from rasa_sdk.forms import FormAction

## Preprocessing: defining the state codes for states and UT
final_states = {'India' : 'TT' , 'Andhra Pradesh': 'AP', 'Arunachal Pradesh': 'AR', 'Assam': 'AS', 'Bihar': 'BR',
                'Chhattisgarh': 'CT', 'Goa': 'GA', 'Gujarat': 'GJ', 'Haryana': 'HR',
                'Himachal Pradesh': 'HP', 'Jharkhand': 'JH', 'Karnataka': 'KA', 'Kerala': 'KL',
                'Madhya Pradesh': 'MP', 'Maharashtra': 'MH', 'Manipur': 'MN', 'Meghalaya': 'ML',
                'Mizoram': 'MZ', 'Nagaland': 'NL', 'Orissa': 'OR', 'Punjab': 'PB', 'Rajasthan': 'RJ',
                'Sikkim': 'SK', 'Tamil Nadu': 'TN', 'Telangana': 'TG', 'Tripura': 'TR', 'Uttarakhand': 'UT',
                'Uttar Pradesh': 'UP', 'West Bengal': 'WB','Chandigarh': 'CH', 'Dadra and Nagar Haveli': 'DN',
                'Delhi': 'DL', 'Ladakh': 'LA', 'Lakshadweep': 'LD', 'Pondicherry': 'PY',
                'Jammu And Kashmir': 'JK', 'Andaman And Nicobar Islands': 'AN', 'Daman And Diu': 'DD'}

def getdataFromAPI():
    ## API URL and the API call we need to do 
    url= "https://data.covid19india.org/v4/min/data.min.json"
    r= requests.get(url = url).json()
    return r

## Custom function for json preprocessing. This will flattend the json for further steps
def flatten_json(y):
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

class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("I am from action file")
        dispatcher.utter_message(text="Hello World response from action.py")
        return []


# class AskLocation(Action):
#     def name(self) -> Text:
#         return "action_ask_location"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         dispatcher.utter_template(tracker, "utter_ask_location")
#         return [FollowupAction(name="action_listen")]

class Action_corona_stat(Action):

    def name(self) -> Text:
        return "action_corona_stat"

    ## This will fetch the given state or districts data provided an input
    def get_sats(self , entity_from_chatbot , flattedDict , state = False):
        res = ""
        for i in flattedDict.keys ():
            if (state == False and len (re.findall(r"(.+?){fname}(.+?)".format(fname=entity_from_chatbot),i)) != 0 ):
                res += str(i) + " " + str(flattedDict[i]) + "\n" 
            ##to get the the total values of only states excluding district
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
        try:
            # entity_from_chatbot = next(tracker.get_latest_entity_values('State'), None)
            if ( next(tracker.get_latest_entity_values('RState'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
            elif ( next(tracker.get_latest_entity_values('LOC'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('LOC'), None)
            elif ( next(tracker.get_latest_entity_values('GPE'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('GPE'), None)
            print ("State to be processed : ", entity_from_chatbot )
        except Exception as e:
            print ( "did not got anything")
        ## API URL and the API call we need to do 
        # url= "https://data.covid19india.org/v4/min/data.min.json"
        # r= requests.get(url = url).json()
        r = getdataFromAPI()
        ## Preprocessing of data. Flattening the dict so that it will work with regex
        flattedDict = flatten_json(r)
        ## The main code that is responsible for serching through the data
        ## This if computes  if the given input is a state or not and searches accordingly
        try:
            if ( entity_from_chatbot.title() in final_states):
                message = self.get_sats(final_states[entity_from_chatbot.title().strip()] , flattedDict , True).replace( final_states[entity_from_chatbot.title()] , entity_from_chatbot.title() )
            else:
                message = self.get_sats(entity_from_chatbot.title().strip() , flattedDict )
                message = message.replace( message[0:2] , get_key(message[0:2] , final_states))
        except Exception as e:
            print ( e)
            dispatcher.utter_message("Sorry we don't have information regarding that place")
        ## giving the output to the chatbot 
        print(message)
        dispatcher.utter_message(message)

class Action_Confirmed_stat(Action):
    def name(self) -> Text:
        return "action_confirmed_stat"
    ## This will fetch the given state or districts data provided an input

    def get_sats(self, entity_from_chatbot, flattedDict, state = False):
        res = ""
        for i in flattedDict.keys ():
            if (state == False and len (re.findall(r"(.+?){fname}_total_confirmed".format(fname=entity_from_chatbot),i)) != 0 ):
                res +=   str(flattedDict[i]) + "\n"
            ##to get the the total values of only states excluding district
            if ( state == True and len (re.findall(r"{fname}_total_confirmed".format(fname=entity_from_chatbot),i)) != 0):
                res +=   str(flattedDict[i]) + "\n" 
        if res == "":
            res += "Data is not available"

        return res

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ## For better output formatting
        def get_key(val , dict_to_search_from):
            for key, value in dict_to_search_from.items():
                if val == value:
                    return key
            return "key doesn't exist" 
        ## To get the slot value from chatbot context. ie: fetching entites
        try:
            # entity_from_chatbot = next(tracker.get_latest_entity_values('State'), None)
            if ( next(tracker.get_latest_entity_values('RState'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
            elif ( next(tracker.get_latest_entity_values('LOC'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('LOC'), None)
            elif ( next(tracker.get_latest_entity_values('GPE'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('GPE'), None)
            print ("State to be processed : ", entity_from_chatbot )
            
            text = tracker.latest_message['text']
            print ( text )
        except Exception as e:
            print ( "did not got anything")
            return []
        ## API URL and the API call we need to do 
        # url= "https://data.covid19india.org/v4/min/data.min.json"
        # r= requests.get(url = url).json()
        r = getdataFromAPI()
        ## Preprocessing of data. Flattening the dict so that it will work with regex
        flattedDict = flatten_json(r)
        ## The main code that is responsible for serching through the data
        ## This if computes  if the given input is a state or not and searches accordingly
        try:
            if ( entity_from_chatbot.title() in final_states):
                # message = self.get_sats(final_states[entity_from_chatbot.title().strip()] , flattedDict , True).replace( final_states[entity_from_chatbot.title()] , entity_from_chatbot.title() )
                message = self.get_sats(final_states[entity_from_chatbot.title().strip()] , flattedDict , True)
            else:
                message = self.get_sats(entity_from_chatbot.title().strip() , flattedDict )
                # message = message.replace("districts" , "")
            print(message)
            dispatcher.utter_message(message) 
            return []    
        except Exception as e:
            print ( e)
            dispatcher.utter_message("Sorry we don't have information regarding that place")
        ## giving the output to the chatbot 



class Action_Death_stat(Action):
    def name(self) -> Text:
        return "action_death_stat"
    ## This will fetch the given state or districts data provided an input

    def get_sats(self, entity_from_chatbot, flattedDict, state = False):
        res = ""
        for i in flattedDict.keys ():
            if (state == False and len (re.findall(r"(.+?){fname}_total_deceased".format(fname=entity_from_chatbot),i)) != 0 ):
                res += "-->  " +  str(flattedDict[i]) + "\n"
            ##to get the the total values of only states excluding district
            if ( state == True and len (re.findall(r"{fname}_total_deceased".format(fname=entity_from_chatbot),i)) != 0):
                res +=  "-->  "  + str(flattedDict[i]) + "\n" 
        if res == "":
            res += "Data is not available for this location"
        return res

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ## For better output formatting
        def get_key(val , dict_to_search_from):
            for key, value in dict_to_search_from.items():
                if val == value:
                    return key
            return "key doesn't exist" 
        ## To get the slot value from chatbot context. ie: fetching entites
        try:
            # entity_from_chatbot = next(tracker.get_latest_entity_values('State'), None)
            if ( next(tracker.get_latest_entity_values('RState'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
            elif ( next(tracker.get_latest_entity_values('LOC'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('LOC'), None)
            elif ( next(tracker.get_latest_entity_values('GPE'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('GPE'), None)
            print ("State to be processed : ", entity_from_chatbot )
        except Exception as e:
            print ( "DID NOT GET ANYTHING")
            return []
        ## API URL and the API call we need to do 
        # url= "https://data.covid19india.org/v4/min/data.min.json"
        # r= requests.get(url = url).json()
        r = getdataFromAPI()
        ## Preprocessing of data. Flattening the dict so that it will work with regex
        flattedDict = flatten_json(r)
        ## The main code that is responsible for serching through the data
        ## This if computes  if the given input is a state or not and searches accordingly
        try:
            if ( entity_from_chatbot.title() in final_states):
                message = self.get_sats(final_states[entity_from_chatbot.title().strip()] , flattedDict , True).replace( final_states[entity_from_chatbot.title()] , entity_from_chatbot.title() )
            else:
                message = self.get_sats(entity_from_chatbot.title().strip() , flattedDict )
                message = message.replace("districts" , "")
        except Exception as e:
            print ( e)
            dispatcher.utter_message("Sorry we don't have information regarding that place")
        ## giving the output to the chatbot 
        print("THIS IS DEATH STATS for ", entity_from_chatbot, " : ",  message)
        dispatcher.utter_message(message) 
        return []


class Action_Recovered_stat(Action):
    def name(self) -> Text:
        return "action_recovered_stat"
    ## This will fetch the given state or districts data provided an input

    def get_sats(self, entity_from_chatbot, flattedDict, state = False):
        res = ""
        for i in flattedDict.keys ():
            if (state == False and len (re.findall(r"(.+?){fname}_total_recovered".format(fname=entity_from_chatbot),i)) != 0 ):
                res += "" + entity_from_chatbot + " : " +  str(flattedDict[i]) + "\n"
            ##to get the the total values of only states excluding district
            if ( state == True and len (re.findall(r"{fname}_total_recovered".format(fname=entity_from_chatbot),i)) != 0):
                res += "" + entity_from_chatbot + " : "  + str(flattedDict[i]) + "\n" 
        if res == "":
            res += "Data is not available"
            
        return res

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ## For better output formatting
        def get_key(val , dict_to_search_from):
            for key, value in dict_to_search_from.items():
                if val == value:
                    return key
            return "key doesn't exist" 
        ## To get the slot value from chatbot context. ie: fetching entites
        try:
            # entity_from_chatbot = next(tracker.get_latest_entity_values('State'), None)
            if ( next(tracker.get_latest_entity_values('RState'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
            elif ( next(tracker.get_latest_entity_values('LOC'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('LOC'), None)
            elif ( next(tracker.get_latest_entity_values('GPE'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('GPE'), None)
            print ("State to be processed : ", entity_from_chatbot )
        except Exception as e:
            print ( "did not got anything")
        ## API URL and the API call we need to do 
        # url= "https://data.covid19india.org/v4/min/data.min.json"
        # r= requests.get(url = url).json()
        r = getdataFromAPI()
        ## Preprocessing of data. Flattening the dict so that it will work with regex
        flattedDict = flatten_json(r)
        ## The main code that is responsible for serching through the data
        ## This if computes  if the given input is a state or not and searches accordingly
        try:
            if ( entity_from_chatbot.title() in final_states):
                message = self.get_sats(final_states[entity_from_chatbot.title().strip()] , flattedDict , True).replace( final_states[entity_from_chatbot.title()] , entity_from_chatbot.title() )
            else:
                message = self.get_sats(entity_from_chatbot.title().strip() , flattedDict )
                message = message.replace("districts" , "")
        except Exception as e:
            print ( e)
            dispatcher.utter_message("Sorry we don't have information regarding that place")
        ## giving the output to the chatbot 
        print(message)
        dispatcher.utter_message(message) 


class Action_Tested_stat(Action):
    def name(self) -> Text:
        return "action_Tested_stat"
    ## This will fetch the given state or districts data provided an input

    def get_sats(self, entity_from_chatbot, flattedDict, state = False):
        res = ""
        for i in flattedDict.keys ():
            if (state == False and len (re.findall(r"(.+?){fname}_total_tested".format(fname=entity_from_chatbot),i)) != 0 ):
                res += "" + entity_from_chatbot + " : " +  str(flattedDict[i]) + "\n"
            ##to get the the total values of only states excluding district
            if ( state == True and len (re.findall(r"{fname}_total_tested".format(fname=entity_from_chatbot),i)) != 0):
                res += "" + entity_from_chatbot + " : "  + str(flattedDict[i]) + "\n" 
        if res == "":
            res += "Data is not available"
            
        return res

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ## For better output formatting
        def get_key(val , dict_to_search_from):
            for key, value in dict_to_search_from.items():
                if val == value:
                    return key
            return "key doesn't exist" 
        ## To get the slot value from chatbot context. ie: fetching entites
        try:
            # entity_from_chatbot = next(tracker.get_latest_entity_values('State'), None)
            if ( next(tracker.get_latest_entity_values('RState'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
            elif ( next(tracker.get_latest_entity_values('LOC'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('LOC'), None)
            elif ( next(tracker.get_latest_entity_values('GPE'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('GPE'), None)
            print ("State to be processed : ", entity_from_chatbot )
        except Exception as e:
            print ( "did not got anything")
        ## API URL and the API call we need to do 
        # url= "https://data.covid19india.org/v4/min/data.min.json"
        # r= requests.get(url = url).json()
        r = getdataFromAPI()
        ## Preprocessing of data. Flattening the dict so that it will work with regex
        flattedDict = flatten_json(r)
        ## The main code that is responsible for serching through the data
        ## This if computes  if the given input is a state or not and searches accordingly
        try:
            if ( entity_from_chatbot.title() in final_states):
                message = self.get_sats(final_states[entity_from_chatbot.title().strip()] , flattedDict , True).replace( final_states[entity_from_chatbot.title()] , entity_from_chatbot.title() )
            else:
                message = self.get_sats(entity_from_chatbot.title().strip() , flattedDict )
                message = message.replace("districts" , "")
        except Exception as e:
            print ( e)
            dispatcher.utter_message("Sorry we don't have information regarding that place")
        ## giving the output to the chatbot 
        print(message)
        dispatcher.utter_message(message) 


class Action_Vaccine_stat(Action):
    def name(self) -> Text:
        return "action_vaccine_stat"
    ## This will fetch the given state or districts data provided an input
    def get_sats(self , entity_from_chatbot , flattedDict , state = False):
        res = ""
        count = 0
        for i in flattedDict.keys ():
            if (state == False and len (re.findall(r"(.+?){fname}_total_vaccinated(.+?)".format(fname=entity_from_chatbot),i)) != 0 ):
                count += 1
                # print ( "This is the str[i] value ", str(i) )
                # print( "\nTHis is the str[flattedDict[i]] value :" , str(flattedDict[i]))
                # res += str(i[2:]) + ": " + str(flattedDict[i]) + "\n"
                res += entity_from_chatbot + "" + str(count) + " : " +  str(flattedDict[i]) + "\n"
            ##to get the the total values of only states excluding district
            if ( state == True and len (re.findall(r"{fname}_total_vaccinated".format(fname=entity_from_chatbot),i)) != 0):
                count += 1
                res += entity_from_chatbot + "" + str(count) + " : "  + str(flattedDict[i]) + "\n" 
        return res.replace("_" , " " ) 
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ## For better output formatting
        def get_key(val , dict_to_search_from):
            for key, value in dict_to_search_from.items():
                if val == value:
                    return key
            return "key doesn't exist" 
        ## To get the slot value from chatbot context. ie: fetching entites
        try:
            # entity_from_chatbot = next(tracker.get_latest_entity_values('State'), None)
            if ( next(tracker.get_latest_entity_values('RState'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
            elif ( next(tracker.get_latest_entity_values('LOC'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('LOC'), None)
            elif ( next(tracker.get_latest_entity_values('GPE'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('GPE'), None)
            print ("State to be processed : ", entity_from_chatbot )
        except Exception as e:
            print ( "did not got anything")
        ## API URL and the API call we need to do 
        # url= "https://data.covid19india.org/v4/min/data.min.json"
        # r= requests.get(url = url).json()
        r = getdataFromAPI()
        ## Preprocessing of data. Flattening the dict so that it will work with regex
        flattedDict = flatten_json(r)
        ## The main code that is responsible for serching through the data
        ## This if computes  if the given input is a state or not and searches accordingly
        try:
            if ( entity_from_chatbot.title() in final_states):
                message = self.get_sats(final_states[entity_from_chatbot.title().strip()] , flattedDict , True).replace( final_states[entity_from_chatbot.title()] , entity_from_chatbot.title() )
            else:
                message = self.get_sats(entity_from_chatbot.title().strip() , flattedDict )
                message = message.replace("districts" , "")
        except Exception as e:
            print ( e)
            dispatcher.utter_message("Sorry we don't have information regarding that place")
        ## giving the output to the chatbot 
        print(message)
        dispatcher.utter_message(message)


class Action_Delta_stat(Action):
    def name(self) -> Text:
        return "action_delta_stat"
    ## This will fetch the given state or districts data provided an input


    def get_sats(self, entity_from_chatbot, flattedDict, state = False):
        res = ""
        for i in flattedDict.keys ():

            if (state == False and len(re.findall(r"(.+?){fname}_delta_confirmed".format(fname=entity_from_chatbot),i)) != 0):
                res += entity_from_chatbot + " : " +  str(flattedDict[i]) + "\n"
            if(state == False and len(re.findall(r"(.+?){fname}_delta21_14_confirmed".format(fname=entity_from_chatbot),i)) != 0):
                res+= entity_from_chatbot + " : " +  str(flattedDict[i]) + "\n"
            if(state == False and len(re.findall(r"(.+?){fname}_delta7_confirmed".format(fname=entity_from_chatbot),i)) != 0):
                res+= entity_from_chatbot + " : " +  str(flattedDict[i]) + "\n"
            ##to get the the total values of only states excluding district
            if ( state == True and len(re.findall(r"{fname}_delta_confirmed".format(fname=entity_from_chatbot),i)) != 0):
                res += entity_from_chatbot + " : "  + str(flattedDict[i]) + "\n"
            if( state == True and len(re.findall(r"{fname}_delta21_14_confirmed".format(fname=entity_from_chatbot),i)) != 0):
                res += entity_from_chatbot + " : " +  str(flattedDict[i]) + "\n"
            if( state == True and len(re.findall(r"{fname}_delta7_confirmed".format(fname=entity_from_chatbot),i)) != 0):
                res += entity_from_chatbot + " : " +  str(flattedDict[i]) + "\n"
        if res == "":
            res += "This Data is not available for this location"
            
        return res
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ## For better output formatting
        def get_key(val , dict_to_search_from):
            for key, value in dict_to_search_from.items():
                if val == value:
                    return key
            return "key doesn't exist" 
        ## To get the slot value from chatbot context. ie: fetching entites
        try:
            # entity_from_chatbot = next(tracker.get_latest_entity_values('State'), None)
            if ( next(tracker.get_latest_entity_values('RState'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
            elif ( next(tracker.get_latest_entity_values('LOC'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('LOC'), None)
            elif ( next(tracker.get_latest_entity_values('GPE'), None) != None):
                entity_from_chatbot = next(tracker.get_latest_entity_values('GPE'), None)
            print ("State to be processed : ", entity_from_chatbot )
        except Exception as e:
            print ( "did not got anything")
        ## API URL and the API call we need to do 
        # url= "https://data.covid19india.org/v4/min/data.min.json"
        # r= requests.get(url = url).json()
        r = getdataFromAPI()
        ## Preprocessing of data. Flattening the dict so that it will work with regex
        flattedDict = flatten_json(r)
        ## The main code that is responsible for serching through the data
        ## This if computes  if the given input is a state or not and searches accordingly
        try:
            if ( entity_from_chatbot.title() in final_states):
                message = self.get_sats(final_states[entity_from_chatbot.title().strip()] , flattedDict , True).replace( final_states[entity_from_chatbot.title()] , entity_from_chatbot.title() )
            else:
                message = self.get_sats(entity_from_chatbot.title().strip() , flattedDict )
                #message = message.replace( message[0:2] , get_key(message[0:2] , final_states))
        except Exception as e:
            print ( e)
            dispatcher.utter_message("Sorry we don't have information regarding that place")
        ## giving the output to the chatbot 
        print(message)
        dispatcher.utter_message(message)


# class ActionReceiveName(Action):

#     def name(self) -> Text:
#         return "action_receive_name"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         text = tracker.latest_message['text']
#         # dispatcher.utter_message(text=f" {text}!")
#         return [SlotSet("RState", text)]



# ##TODO:THis has been changed so work carefully
# class Action_Death_form(FormAction):
#     def name(self) -> Text:
#         return "action_death_form"
#     ## This will fetch the given state or districts data provided an input

#     @staticmethod
#     def required_slots(tracker: Tracker) -> List[Text]:
#         return ["FState"]
    
#     def get_sats(self, entity_from_chatbot, flattedDict, state = False):
#         res = ""
#         for i in flattedDict.keys ():
#             if (state == False and len (re.findall(r"(.+?){fname}_total_deceased".format(fname=entity_from_chatbot),i)) != 0 ):
#                 res += "" + entity_from_chatbot + " : " +  str(flattedDict[i]) + "\n"
#             ##to get the the total values of only states excluding district
#             if ( state == True and len (re.findall(r"{fname}_total_deceased".format(fname=entity_from_chatbot),i)) != 0):
#                 res += "" + entity_from_chatbot + " : "  + str(flattedDict[i]) + "\n" 
#         if res == "":
#             res += "Data is not available"
            
#         return res

#     def submit(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         ## For better output formatting
#         def get_key(val , dict_to_search_from):
#             for key, value in dict_to_search_from.items():
#                 if val == value:
#                     return key
#             return "key doesn't exist" 
#         ## To get the slot value from chatbot context. ie: fetching entites
#         try:
#             # entity_from_chatbot = next(tracker.get_latest_entity_values('State'), None)
#             if ( next(tracker.get_latest_entity_values('RState'), None) != None):
#                 entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
#             elif ( next(tracker.get_latest_entity_values('FState'), None) != None):
#                 entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
#             elif ( next(tracker.get_latest_entity_values('FStates'), None) != None):
#                 entity_from_chatbot = next(tracker.get_latest_entity_values('RState'), None)
#             elif ( next(tracker.get_latest_entity_values('LOC'), None) != None):
#                 entity_from_chatbot = next(tracker.get_latest_entity_values('LOC'), None)
#             elif ( next(tracker.get_latest_entity_values('GPE'), None) != None):
#                 entity_from_chatbot = next(tracker.get_latest_entity_values('GPE'), None)
#             print ("State to be processed : ", entity_from_chatbot )
#         except Exception as e:
#             print ( "did not got anything")
#         ## API URL and the API call we need to do 
#         # url= "https://data.covid19india.org/v4/min/data.min.json"
#         # r= requests.get(url = url).json()
#         r = getdataFromAPI()
#         ## Preprocessing of data. Flattening the dict so that it will work with regex
#         flattedDict = flatten_json(r)
#         ## The main code that is responsible for serching through the data
#         ## This if computes  if the given input is a state or not and searches accordingly
#         try:
#             if ( entity_from_chatbot.title() in final_states):
#                 message = self.get_sats(final_states[entity_from_chatbot.title().strip()] , flattedDict , True).replace( final_states[entity_from_chatbot.title()] , entity_from_chatbot.title() )
#             else:
#                 message = self.get_sats(entity_from_chatbot.title().strip() , flattedDict )
#                 message = message.replace("districts" , "")
#         except Exception as e:
#             print ( e)
#             dispatcher.utter_message("Sorry we don't have information regarding that place")
#         ## giving the output to the chatbot 
#         print(message)
#         dispatcher.utter_message(message) 


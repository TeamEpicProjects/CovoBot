# COVOBOT

### PROBLEM STATEMENT:
CovoBot, is a real life chatbot which is developed to help consumers to be aware of every single information about this pandemic. A user should be able to communicate with the bot anytime and should be able to get the latest status on COVID-19. It is a Basic Conversational integrated with Covid-19 Trackers API’S to get real time details of cases across India, and eventually a simple communication channel that a user can use for conversations. 

### FEATURES:
A chatbot built using RASA, to answer queries related to COVID-19, its symptoms, precautions, and queries related to the vaccines, its complications, side effects, doses, dates, etc. This product will act as a bot to communicate with users using a chat interface such as Slack or Telegram and will be able to understand user intention, manage conversation flow, and be able to retrieve answers using some external knowledge base of API. Concepts of Natural Language Processing and Python to develop the chatbot, where we develop intents, entities, stories, actions (these are the requirements for the working of RASA).
Various natural language processing algorithms were used to process datasets. The chatbot answers questions, with the RASA framework and uses DIET Classifier for better intent classification.


### OBJECTIVE:
- Installing and setting up Rasa Chatbot framework. 
- Create Training Data for NLU. Train NLU model using RASA. Test performance of NLU. 
- Using public API develop a local API to fetch COVID related information. Using unstructured data trained ML/DL model to get unstructured text-based answers. Testing conversational system.
- Creating Training Data for conversational stories. Training the dialog system. Testing conversational system.
- Final delivery of project, Integration with Slack. Documentation and presentation.

### Backend API’s:
https://data.covid19india.org/v4/min/data.min.json

### Flow diagram of the project
![image](https://user-images.githubusercontent.com/76863190/135246982-2da635c2-faf2-4f38-a3b0-365bf97e344e.png)


### TECHNOLOGY STACK:
| Tools | Description |
| ------ | ------ |
| Jupyter | Open-source IDE used for development |
| Python 3.7 |Python 3.7	An interpreted high-level general-purpose programming language |
| RASA | It is a tool to build custom AI chatbots using Python and natural language understanding (NLU). |
| SpaCy | SpaCy	It is used for pre-processing of the utterances, tokenization, and featurization. |
| DIET classifiers | Dual Intent Entity Transformer (DIET) used for intent classification and entity extraction |
| TensorFlow | open-source software library for machine learning and artificial intelligence |
| NLTK | NLTK	The Natural Language Toolkit (NLTK) a standard python library with prebuilt functions and utilities for the ease of use and implementation |
| Telegram |Telegram	It is a free and open source, cross-platform, cloud-based instant messaging software. |
| Requests/urllib | Requests/urllib |

### CONCLUSION
In this project, an artificially intelligent chatbot is developed to answer questions on COVID-19 utilising natural language processing, rasa, and machine learning. Datasets were processed using a variety of natural language processing methods. An artificial neural network is used to build the model, and it is trained using processed data so that our chatbot can provide the right response. The chatbot is evaluated by putting it to the test with a diverse collection of queries. Also, as the dataset grows, the chatbot's accuracy is expected to improve.

#### PRESENTATION LINK:
https://www.canva.com/design/DAEpxnotnJg/7Bzui_iULYmdhzMfXuq2mA/view?utm_content=DAEpxnotnJg&utm_campaign=designshare&utm_medium=link&utm_source=sharebutton

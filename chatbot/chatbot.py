##################
# Author: james putterman
# just plyaing around
# not intended for production
# add more cool things
##################

#!/usr/bin/env python3

# load libraries
import os
import json
import apiai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client


#Load credentials from environment

#Twilio
ACCOUNT_NUM = os.environ['TWILIO_ACCOUNT_NUMBER']
ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']

#API AI
CLIENT_ACCESS_TOKEN = os.environ['CLIENT_ACCESS_TOKEN']

#NASA
nasa_key = '?api_key=DEMO_KEY'

#create Twilio Client object
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Create APIAI object
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

#nasa api url/key
apod_url = 'https://api.nasa.gov/planetary/apod'

#quote api url
quote_url = 'https://api.quotable.io/random'

#catfacts api url
catfact_url = 'https://catfact.ninja/facts?limit=1&max_length=140'

app = Flask(__name__)


@app.route('/sms', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    if 'quote' in incoming_msg:
        # return a quote
        r = request.get(quote_url)
        if r.status_code == 200:
            data = r.json()
            quote = f'{data["content"]} ({data["author"]})'
        else:
            quote = 'I could not retrieve a quote at this time, sorry.'
        msg.body(quote)
        responded = True
    if 'cat' in incoming_msg:
        # return a cat pic
        msg.media('https://cataas.com/cat')
        responded = True
    if 'catfact' in incoming_msg:
        #return a hot fact about cats
        response = request.get(catfact_url)
        if response.status_code == 200:
            result = json.loads(response.text)
            p = result['data']
            fact = p[0]['fact']
            msg.body(fact)
            responded = True
        else:
            msg.body = ('I couldn''t get a cat fact right now, try again later.')
            responded = True
    if 'space' in incoming_msg:
        response = request.get(apod_url + nasa_key)
        if response.status_code == 200:
            data = response.json()
            msg.body(f'{data["date"]} {data["explanation"]}')
            msg.media(data["hdurl"])
            responded = True
        else:
            msg.body('Sorry, I couldn''t get a space pic right now, try again later')
            responded = True
        #responded = True
    if 'baby yoda' in incoming_msg:
        msg.body('https://www.youtube.com/results?search_query=baby+yoda')
        responded = True
    if not responded:
        # get SMS metadata
        msg_from = request.values.get("From", None)
        msg = request.values.get("Body", None)

        # prepare API.ai request
        req = ai.text_request()
        req.lang = 'en'  # optional, default value equal 'en'
        req.query = msg

        # get response from API.ai
        api_response = req.getresponse()
        responsestr = api_response.read().decode('utf-8')
        response_obj = json.loads(responsestr)

        if 'result' in response_obj:
            response = response_obj["result"]["fulfillment"]["speech"]
            # send SMS response back via twilio
            resp = client.messages.create(to=msg_from, from_= ACCOUNT_NUM, body=response)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
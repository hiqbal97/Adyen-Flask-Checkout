import Adyen
import json
import uuid
import os
from dotenv import load_dotenv, find_dotenv
import random
from urllib.parse import urlparse
import string
import random
import requests

load_dotenv(find_dotenv())

reference = str(uuid.uuid1())
currentState = 0

def new_ref():
    global reference
    reference = str(uuid.uuid1())
    return(reference)

def session(currency, amount, country, shopper, url):  
    adyen = Adyen.Adyen()
    adyen.payment.client.xapikey = os.environ.get('ADYEN_API_KEY')
    adyen.payment.client.platform = 'test'
    adyen.payment.client.merchant_account = os.environ.get('ADYEN_MERCHANT_ACCOUNT')
    global currentState
    currentState = 0
    request = {}
    amount = int(amount)
    if shopper:
        request['shopperReference'] = shopper
        request['shopperInteraction'] = 'ContAuth'
        request['recurringProcessingModel'] = 'CardOnFile'
    else:
        shopper = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        request['shopperReference'] = shopper
        request['shopperInteraction'] = 'Ecommerce'
        request['recurringProcessingModel'] = 'CardOnFile'
        request['storePaymentMethod'] = True
    new_ref()
    request['amount'] = {'value': amount, 'currency': currency}
    request['reference'] = str(reference)
    request['returnUrl'] = f'{url}redirect?shopperOrder=myRef'
    request['countryCode'] = country
    result = adyen.checkout.sessions(request)
    result = json.dumps((json.loads(result.raw_response)))
    print(result)
    return(result)

def get_reference():
    return(reference)

def modifications(amount, currency, type, psp):
    amount = int(amount)
    new_ref()
    headers = {
        'x-api-key': os.environ.get('ADYEN_API_KEY'),
    }
    if type == 'cancel':
        json_data = {
        'merchantAccount': os.environ.get('ADYEN_MERCHANT_ACCOUNT'),
        'reference': reference,
    }
    else:
        json_data = {
            'merchantAccount': os.environ.get('ADYEN_MERCHANT_ACCOUNT'),
            'amount': {
                'currency': currency,
                'value': amount,
            },
            'reference': reference,
        }
    response = requests.post(f'https://checkout-test.adyen.com/v68/payments/{psp}/{type}s', headers=headers, json=json_data)
    print(response.text)
    return(response.text)

def currentState():
    return(currentState)

def getMethods(currency, amount, country):
    adyen = Adyen.Adyen()
    adyen.payment.client.platform = 'test'
    adyen.client.xapikey = os.environ.get('ADYEN_API_KEY')
    amount = int(amount)
    request = {
        'countryCode': country,
        'amount': {
            'value': amount,
            'currency': currency
        },
        'channel': 'Web',
        'merchantAccount': os.environ.get('ADYEN_MERCHANT_ACCOUNT')
    }
    result = adyen.checkout.payment_methods(request)
    global methods
    methods = result
    result = json.dumps((json.loads(result.raw_response)))
    return(result)

def makePayment(currency, amount, country, state_data, url):
    adyen = Adyen.Adyen()
    adyen.payment.client.platform = 'test'
    adyen.client.xapikey = os.environ.get('ADYEN_API_KEY')
    global currentState
    currentState = 1
    new_ref()
    request = {
        'paymentMethod': state_data,
        'amount': {
            'value': amount,
            'currency': currency
        },
        'reference': reference,
        'countryCode': country,
        'returnUrl': f'{url}redirect?shopperOrder=myRef',
        'merchantAccount': os.environ.get('ADYEN_MERCHANT_ACCOUNT')
    }
    request.update(state_data.get_json())
    result = adyen.checkout.payments(request)
    result = json.dumps((json.loads(result.raw_response)))
    print(result)
    return(result)

def paymentDetails(state_data, redirect):
    adyen = Adyen.Adyen()
    adyen.payment.client.platform = 'test'
    adyen.client.xapikey = os.environ.get('ADYEN_API_KEY')
    if redirect:
        result = adyen.checkout.payments_details(state_data)
    else:
        result = adyen.checkout.payments_details(state_data.get_json())
    result = json.loads(result.raw_response)
    return(result)
from random import choices
import requests
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired
from adyen_api import session, get_reference, getMethods, makePayment, paymentDetails, currentState, modifications
import os
import json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
app = Flask(__name__)

app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'
Bootstrap(app)

class Details(FlaskForm):
    amount = FloatField('What is the amount?', validators=[DataRequired()])
    code = StringField('What is the currency?', validators=[DataRequired()])
    country = StringField('What is the country code?')
    shopper = StringField('Enter a shopper reference')
    submit = SubmitField('Checkout')

class Mods(FlaskForm):
    options = SelectField('Select the modifications you want to make', choices=['capture', 'cancel', 'refund'], validators=[DataRequired()])
    psp = StringField('What is the pspReference?', validators=[DataRequired()])
    amount = FloatField('What is the amount?')
    code = StringField('What is the currency?')
    submit = SubmitField('Submit')

@app.route('/mods', methods=['GET', 'POST'])
def mods():
    form = Mods()
    if form.validate_on_submit():
        global options
        options = form.options.data
        global currency
        currency = form.code.data
        global amount
        amount = (form.amount.data*100)
        global psp
        psp = form.psp.data
        return redirect(url_for('modRequest'))
    return render_template('mods.html', form=form)

@app.route('/response')
def modRequest():
    response = modifications(amount, currency, options, psp)
    return render_template('mods_result.html', response=response)

@app.route('/', methods=['GET', 'POST'])
def home():
    form = Details()
    if form.validate_on_submit():
        global currency
        currency = form.code.data
        global amount
        amount = (form.amount.data*100)
        global country
        country = form.country.data
        global shopper
        shopper = form.shopper.data
        return redirect(url_for('checkout'))
    return render_template('index.html', form=form)

@app.route('/checkout')
def checkout():
    return render_template('dropin.html', client_key=os.environ.get('ADYEN_CLIENT_KEY'))

@app.route('/api/sessions', methods=['POST'])
def sessions():
    url = request.host_url
    return session(currency, amount, country, shopper, url)

@app.route('/redirect', methods=['POST', 'GET'])
def redirected():
    if currentState() == 0:
        return render_template('dropin.html', client_key=os.environ.get('ADYEN_CLIENT_KEY'))
    elif currentState() == 1:
        headers = request.values.to_dict()
        parsed = {}
        parsed['details'] = {'redirectResult': headers['redirectResult']}
        result = paymentDetails(parsed, True)
        if result['resultCode'] == 'Authorised' or result['resultCode'] == 'Received' or result['resultCode'] == 'Pending':
            return redirect(url_for('success'))
        else:
            return redirect(url_for('failed'))

@app.route('/result/success')
def success():
    ref = get_reference()
    return render_template('success.html', ref=ref)

@app.route('/result/failed')
def failed():
    ref = get_reference()
    return render_template('failed.html', ref=ref)

@app.route('/api/methods', methods=['POST'])
def getPaymentMethods():
    return getMethods(currency, amount, country)

@app.route('/api/makePayment', methods=['POST'])
def pay():
    url = request.host_url
    return makePayment(currency, amount, country, request, url)

@app.route('/api/details', methods=['POST'])
def additional():
    print(request)
    return paymentDetails(request, False)

@app.route('/old', methods=['GET', 'POST'])
def old():
    form = Details()
    if form.validate_on_submit():
        global currency
        currency = form.code.data
        global amount
        amount = (form.amount.data*100)
        global country
        country = form.country.data
        global shopper
        shopper = form.shopper.data
        return redirect(url_for('oldCheckout'))
    return render_template('old.html', form=form)

@app.route('/old/checkout')
def oldCheckout():
    return render_template('dropin_old.html', client_key=os.environ.get('ADYEN_CLIENT_KEY'))

if __name__ == '__main__':
    app.run(port=8080, debug=True)
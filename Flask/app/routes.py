import json
import hashlib
import requests
from app import app
from flask import session, render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RequestForm, PaymentForm
from werkzeug.security import generate_password_hash, check_password_hash
from requests import post
userdata = { 'sidharth' : {
                            'pass' : 'pbkdf2:sha256:50000$6pMVycvT$8e8964c84ac54e1493adb8af16fd855a3c255aea36b9f94edadfe093adece24f',
                            'port' : 5000,
                            'host' : '127.0.0.1',
			    'goods_request': [ ], 
			    'payment_request' : [ ],
			    'payment_sent' : [ ],
			    'requested_hash' : [ ], 
			    'sent_hash' : [ ] ,
			    'received_hash' : [ ] 

                        },
            'shivang' : {
                            'pass' : 'pbkdf2:sha256:50000$aZdGam1Y$3c0643e3ba81ceb3642d764be870413b85d649c69de9bd95bb5db9c8fa5a22fe',
                            'port' : 5500,
                            'host' : '127.0.0.1',
			    'goods_request': [ ], 
			    'payment_request' : [ ],
			    'payment_sent' : [ ],
			    'requested_hash' : [ ], 
			    'sent_hash' : [ ] ,
			    'received_hash' : [ ] 
                        },
            'hamza' : {
                            'pass' : 'pbkdf2:sha256:50000$rmdDuDNr$cdee93d359041e9cd268800c16234dedb0ffa460f43193ac6855f97894a6ae64',
                            'port' : 6000,
                            'host' : '127.0.0.1',
			    'goods_request': [ ], 
			    'payment_request' : [ ],
			    'payment_sent' : [ ],
			    'requested_hash' : [ ], 
			    'sent_hash' : [ ] ,
			    'received_hash' : [ ] 
                      }
            }
validater_data="http://127.0.0.1:5001"
@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    print(str(userdata[session['username']]['goods_request']))
    return render_template('index.html', title='BlockChainApp', user=session['username'], goods_request=userdata[session['username']]['goods_request'], payment_request=userdata[session['username']]['payment_request'], payment_sent=userdata[session['username']]['payment_sent'])

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data in userdata.keys():
            if check_password_hash( userdata[form.username.data]['pass'] , form.password.data):
                session['username'] = form.username.data
                return redirect(url_for('index'))
            else:
                flash('Password incorrect.')
        else:
            flash('Username not registered.')

    return render_template('login.html', title='Sign In', form=form)
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/request_goods', methods = ['GET', 'POST'])
def request_goods():
    form = RequestForm()
    formDict = {} 
    if (form.validate_on_submit()) :
        formDict['product1'] = form.product1.data
        formDict['quantity1'] = form.quantity1.data
        formDict['product2'] = form.product2.data
        formDict['quantity2'] = form.quantity2.data
        url = 'http://' + userdata[form.To.data]['host'] + ':' + str(userdata[form.To.data]['port']) + '/update'
        request_hash = hash(formDict)
        #update requested_hash for the current user
        userdata[session['username']]['requested_hash'].append(request_hash)
        from_to_hash = concat(form.To.data, session['username'])
        hashr = post(url = validater_data+'/Manu/Request', data = {'supplier_manu': from_to_hash, 'requested_hash' : request_hash })
        formDict['Type'] = 'goods_request'
        formDict['From'] = session['username']
        formDict['To'] = form.To.data
        r = post(url = url, data = formDict )
        if(r.status_code == 200):
            return 'Goods Request Sent'
        else:
            return 'Error in Sending'
    return render_template('request.html', title='Request', form=form)

@app.route('/update', methods = ['POST'])
def update():
    updateDict = dict(request.form)
    for key in updateDict.keys():
        val = updateDict[key][0]
        updateDict[key] = val
    updateType = updateDict['Type']
    print(str(updateDict))
    userdata[updateDict['To']][updateType].append(updateDict)
    return str(updateDict)


@app.route('/send_goods', methods = ['GET', 'POST'])
def send_goods():
    form = RequestForm()
    formDict = {} 
    if (form.validate_on_submit()) :
        formDict['product1'] = form.product1.data
        formDict['quantity1'] = form.quantity1.data
        formDict['product2'] = form.product2.data
        formDict['quantity2'] = form.quantity2.data
        sent_hash = hash(formDict)
        supplier_manu= concat(form.To.data, session['username'])
        #update sent_hash for the current user
        userdata[session['username']]['sent_hash'].append(sent_hash)
        hashr = post(url = validater_data+'/Supplier/Sent', data = {'supplier_manu': supplier_manu, 'sent_hash' : sent_hash, 'requested_payment' : form.payment.data})
        payment = {}
        payment['From'] = session['username']
        payment['To'] = form.To.data
        payment['Type'] = 'payment_request'
        payment['payment_request'] = form.payment.data
        url = 'http://' + userdata[form.To.data]['host'] + ':' + str(userdata[form.To.data]['port']) + '/update'
        r = post(url = url, data = payment )
        userdata[session['username']]['goods_request'].pop(0)
        if(r.status_code == 200):
            return 'Payment Request Sent'
        else:
            return 'Error in Sending'
        
    return render_template('request.html', title='Request', form=form, payment=True)

@app.route('/receive_goods', methods = ['GET', 'POST'])
def receive_goods():
    form = RequestForm()
    formDict = {} 
    if (form.validate_on_submit()) :
        formDict['product1'] = form.product1.data
        formDict['quantity1'] = form.quantity1.data
        formDict['product2'] = form.product2.data
        formDict['quantity2'] = form.quantity2.data
        received_hash = hash(formDict)
        supplier_manu= concat(form.To.data, session['username'])
        #update sent_hash for the current user
        userdata[session['username']]['received_hash'].append(received_hash)
        hashr = post(url = validater_data+'/Manu/Received', data = {'supplier_manu': supplier_manu, 'received_hash' : received_hash })
        return 'Goods Recieved. Try sending payment to see if goods received are authentic.'
    return render_template('request.html', title= 'Receive', form=form)

@app.route('/send_payment', methods=['GET', 'POST'])
def send_payment():
    form = PaymentForm()
    formDict = {}
    if (form.validate_on_submit()) :
        To = form.To.data
        Success = True
        req_hash = userdata[session['username']]['requested_hash']
        rec_hash = userdata[session['username']]['received_hash']
        print(req_hash, end='*')
        print(rec_hash, end='*')
        if len(req_hash) == 0 :
            return 'Transaction Failiure no request sent'
        if req_hash[0] not in rec_hash:
            Success = False
        userdata[session['username']]['payment_request'].pop(0)
        userdata[session['username']]['received_hash'].pop(0)
        userdata[session['username']]['requested_hash'].pop(0)
        if Success : 
            formDict['To'] = form.To.data
            formDict['From'] = session['username']
            formDict['Payment'] = form.payment.data
            formDict['Type'] = 'payment_sent'
            supplier_manu = concat(form.To.data, session['username'])
            url = 'http://' + userdata[form.To.data]['host'] + ':' + str(userdata[form.To.data]['port']) + '/update'
            r = post(url = url, data = formDict) 
            hashr = post(url = validater_data+'/Manu/Sent', data = {'supplier_manu': supplier_manu, 'sent_payment' : form.payment.data })
            
            return 'Payment Sent'
        return 'Transaction Failiure: requested_hash and received_hash not matching.'
    return render_template('/payment.html', title='Send Payment',form=form)

@app.route('/receive_payment', methods = ['GET', 'POST'])
def receive_payment():
    form = PaymentForm()
    formDict = {}
    if (form.validate_on_submit()) :
        supplier_manu = concat(form.To.data, session['username'])
        url = 'http://' + userdata[form.To.data]['host'] + ':' + str(userdata[form.To.data]['port']) + '/update'
        hashr = post(url = validater_data+'/Supplier/Received', data = {'supplier_manu': supplier_manu, 'received_payment' : form.payment.data })
        if(len(userdata[session['username']]['payment_sent']) == 0) :
            return 'No Payments sent for recieving'
        userdata[session['username']]['payment_sent'].pop(0) 
        userdata[session['username']]['sent_hash'].pop(0) 
        return 'Payment Recieved Acknowledged'
    return render_template('/payment.html', title = 'Recieve Payment', form=form)

def hash(dictionary):
    dict_string = json.dumps(dictionary, sort_keys=True).encode()
    return hashlib.sha256(dict_string).hexdigest()

def concat(a, b):
    string = ''
    if a < b:
        string = a + b
    else:
        string = b + a
    return string

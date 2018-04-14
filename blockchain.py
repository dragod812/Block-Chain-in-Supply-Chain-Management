from time import time
import json
import hashlib
from flask import Flask, jsonify ,request
from uuid import uuid4
from urllib.parse import urlparse
import requests

class Blockchain():
    def __init__(self):
        #Initializes the instance variables of the Blockchain class.
        self.chain=[]
        self.current_transactions={}
        self.nodes=set()
        self.to_be_mined={}
        self.new_block(proof=100,previous_hash=1)
        

    def register_node(self,address):
        #Registers the address of a new node.
        parsed_url=urlparse(address)
        self.nodes.add(parsed_url.netloc)


    def new_block(self,proof,previous_hash=None):
        #Adds new block to existing chain.
        block={
            'index':len(self.chain),
            'timestamp':time(),
            'transactions':self.to_be_mined,
            'proof':proof,
            'previous_hash':previous_hash
            }
        self.to_be_mined={}
        self.chain.append(block)
        return block


    def new_transaction(self,supplier_manu,requested_hash=None,sent_hash=None,received_hash=None,requested_payment=None,sent_payment=None,received_payment=None):
        #Adds a transaction to the list of current transactions to be
        #added to the next block .Returns the index of the block the
        #transaction is going to be added to.
        key=supplier_manu
        if(key not in self.current_transactions ):
            self.current_transactions[key]={}
        if(requested_hash):
            self.current_transactions[key]['requested_hash']=requested_hash
        if(sent_hash):
            self.current_transactions[key]['sent_hash']=sent_hash
        if(received_hash):
            self.current_transactions[key]['received_hash']=received_hash
        if(requested_payment):
            self.current_transactions[key]['requested_payment']=requested_payment
        if(sent_payment):
            self.current_transactions[key]['sent_payment']=sent_payment
        if(received_payment):
            self.current_transactions[key]['received_payment']=received_payment
        
        return self.last_block['index']+1
    

    def proof_of_work(self,last_proof):
        #calculates the valid proof using our Proof Of Work Algorithm
        proof=0
        while not self.valid_proof(proof,last_proof) :
            proof=proof+1

        return proof
    

    def valid_chain(self,chain):
        #Function to check if a chain is valid
        #(checks the hashes and the proof of works of all the blocks of a chain)
        #Returns True if valid chain else returns False
        curr_block=chain[0]
        last_proof=curr_block['proof']
        last_hash=self.hash(curr_block)
        for i in range(1,len(chain)):
            curr_block=chain[i]
            if(curr_block['previous_hash']!=last_hash):
                return False
            if(not self.valid_proof(curr_block['proof'],last_proof)):
                return False
            last_proof=curr_block['proof']
            last_hash=self.hash(curr_block)

        return True

    def mine(self):
        last_block=self.last_block
        last_proof=last_block['proof']
        proof=self.proof_of_work(last_proof)
        #blockchain.new_transaction(sender="0",reciever=node_id,amount=1)
        prev_hash=self.hash(last_block)
        new_block=self.new_block(proof,prev_hash)


    def consensus(self):
        #Consensus algorithm implementation
        #Gets the longest valid chain among all the nodes.
        #Returns True if chain is changed and False if not.
        all_nodes=self.nodes
        max_chain_length=len(self.chain)
        new_chain=None
        for node in all_nodes:
            response=requests.get(f'http://{node}/chain')
            if response.status_code==200:
                length=response.json()['length']
                chain=response.json()['chain']
                if length>max_chain_length and self.valid_chain(chain) :
                    max_chain_length=length
                    new_chain=chain

        if new_chain:
            self.chain=new_chain
            return True

        return False

    def check_transactions(self,supplier_manu):
        temp=self.current_transactions.pop(supplier_manu,None)
        if(temp['requested_hash']==temp['sent_hash']
           and temp['sent_hash']==temp['received_hash']
           and temp['requested_payment']==temp['sent_payment']
           and temp['sent_payment']==temp['received_payment']):
            self.to_be_mined[supplier_manu]=temp
            self.mine()
            return True
        return False
    
            
                    
    @staticmethod
    def valid_proof(proof,last_proof):
        #Returns True if a proof of work is valid else returns False.
        #For proof to be valid , when hashed with the last proof ,
        #the result should have four zeros at the end (0000) .
        temp=f'{last_proof}{proof}'.encode()
        temp=hashlib.sha256(temp).hexdigest()
        if(temp[:4])=="0000":
            return True
        else :
            return False
        

    @staticmethod
    def hash(block):
        #Calculates the hash of a block using the SHA256 algorithm.
        #Returns the hash in hexadecimal.
        block=json.dumps(block,sort_keys=True).encode()#needs to be encoded because hashlib.sha256() can only hash bytes .
        return hashlib.sha256(block).hexdigest()


    @property
    def last_block(self):
        #returns the last block of the chain.
        return self.chain[-1]
    

app=Flask(__name__)#Making blockchain API using Flask microframework

node_id=str(uuid4()).replace('-','')

blockchain=Blockchain()

#Whenever we want to register new nodes , we send a post request
#to the server at /nodes/register relative URL with the address
#of the node in the POST request's body.
@app.route('/nodes/register',methods=['POST'])
def register():
    values=request.get_json()
    nodes=values.get("nodes")
    if nodes is None:
        return "Error",400
    for node in nodes:
        blockchain.register_node(node)
    response={
        'message':'New nodes have been added',
        'nodes_list':list(blockchain.nodes)
        }
    return jsonify(response),201

#If we want to create a consensus about the validity of the current
#blockchain , we send a GET request at the /nodes/resolve relative
#URL . It uses the Blockchain.consensus() method to download the chains
#of all the nodes in the network and sets the longest valid chain as the
#correct chain.
@app.route('/nodes/resolve',methods=['GET'])
def resolve():
    temp=blockchain.consensus()
    response={}
    if temp:
        response={
            'message':'Chain was replaced',
            'chain':blockchain.chain
            }
    else :
        response={
            'message':'Chain not replaced',
            'chain':blockchain.chain
            }

    return jsonify(response),200


#Simply retrieves the current copy of the blockchain at the node by sending
#a GET request at /chain relative URL.
@app.route('/chain',methods=['GET'])
def full_chain():
    response={
        'chain':blockchain.chain,
        'length':len(blockchain.chain)
        }
    return jsonify(response),200

@app.route('/Manu/Request',methods=['POST'])
def manu_request():
    values=request.form
    required=['supplier_manu','requested_hash']
    if not all(k in values for k in required):
        return "Missing Data",400
    index=blockchain.new_transaction(values['supplier_manu'],requested_hash=values['requested_hash'])
    response={'message':f'Manufacturer has sent request'}
    return jsonify(response),201

@app.route('/Supplier/Sent',methods=['POST'])
def supplier_sent():
    values=request.form
    required=['supplier_manu','sent_hash','requested_payment']
    if not all(k in values for k in required):
        return "Missing Data",400
    index=blockchain.new_transaction(values['supplier_manu'],sent_hash=values['sent_hash'],requested_payment=values['requested_payment'])
    response={'message':f'Supplier has sent requested goods and payment request to manufacturer'}
    return jsonify(response),201

@app.route('/Manu/Received',methods=['POST'])
def manu_received():
    values=request.form
    required=['supplier_manu','received_hash']
    if not all(k in values for k in required):
        return "Missing Data",400
    index=blockchain.new_transaction(values['supplier_manu'],received_hash=values['received_hash'])
    response={'message':f'Manufacturer has received the sent goods'}
    return jsonify(response),201

@app.route('/Manu/Sent',methods=['POST'])
def manu_sent():
    values=request.form
    required=['supplier_manu','sent_payment']
    if not all(k in values for k in required):
        return "Missing Data",400
    index=blockchain.new_transaction(values['supplier_manu'],sent_payment=values['sent_payment'])
    response={'message':f'Manufacturer has sent the requested payment to the supplier'}
    return jsonify(response),201

@app.route('/Supplier/Received',methods=['POST'])
def Supplier_received():
    values=request.form
    required=['supplier_manu','received_payment']
    if not all(k in values for k in required):
        return "Missing Data",400
    index=blockchain.new_transaction(values['supplier_manu'],received_payment=values['received_payment'])
    temp=blockchain.check_transactions(values['supplier_manu'])
    if temp :
        response={'message':f'block has beeb mined'}
        return jsonify(response),200
    else:
        response={'message':f'transaction has been cancelled'}
        return jsonify(response),200


@app.route('/test',methods=['GET'])
def test():
    response={
        'current_transactions':blockchain.current_transactions
        }
    return jsonify(response),200

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)






        

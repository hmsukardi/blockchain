import sys
import hashlib
import json

from time import time
from uuid import uuid4

from flask import flask
from flask.globals import request
from flask.json import jsonify

import requests
from urllib.parse import urlparse

class Blockchain(object):
    difficulty_target = "0000"

    def hash_block(self, block):
        block_encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest()

    def __init__(self):
        self.chain = []

        self.current_transaction = []

        genesis_hash = self.hash_block("genesis_block")

        self.append_block(
            hash_of_previous_block = genesis_hash,
            nonce = self.proof_of_work(0, genesis_hash, [])
        )

    def proof_of_work(self, index, hash_of_previous_block, transaction, nonce):
        nonce = 0

        while self.valid_proof(index, hash_of_previous_block, transaction, nonce) is False:
            nonce += 1
        return nonce
        
    def valid_proof(self, index, hash_of_previous_block, transaction, nonce):
        content = f'{index}{hash_of_previous_block}{transaction}{nonce}'.encode()

        content_hash = hashlib.sha256(content).hexdigest()

        return content_hash[:len(self.difficulty_target)] == self.difficulty_target

    def append_block(self, nonce, hash_of_previous_block):
        block = {
            'index' : len(self.chain),
            'timestamp' : time(),
            'transaction' : self.current_transaction,
            'nonce' : nonce,
            'hash_of_previous_block' : hash_of_previous_block
        }

        self.current_transaction = []

        self.chain.append(block)
        return block

    def add_transaction(self, sender, recepient, amount):
        self.current_transaction.append({
            'amount': amount,
            'recepient': recepient,
            'sender': sender
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', "")

blockchain = Blockchain()

#routes
@app.route('/blockchain', method=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route('/mine', method=['GET'])
def mine_block():
    blockchain.add_transaction(
        sender="0",
        recepient=node_identifier,
        amount=1
    )

    last_block_hash = blockchain.hash_block(blockchain.last_block)

    index = len(blockchain.chain)
    nonce = blockchain.proof_of_work(index, last_block_hash, blockchain.current_transaction)

    block = blockchain.append_block(nonce, last_block_hash)
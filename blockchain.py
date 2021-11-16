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

    def proof_of_work(self, index, hash_of_proof_of_work, transaction, nonce):
        nonce = 0

        while self.valid_proof(index, hash_of_proof_of_work, transaction, nonce) is False:
            nonce += 1
        return nonce
        
import hashlib
import json
from time import time
from cryptography.fernet import Fernet
import os

class SimpleBlockchain:
    def __init__(self, encryption_key):
        self.chain = []
        self.key = encryption_key
        self.cipher = Fernet(self.key)
        self.create_block(previous_hash='0')

    def create_block(self, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'data': [],
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        return block

    def encrypt_data(self, data):
        json_str = json.dumps(data)
        encrypted = self.cipher.encrypt(json_str.encode())
        return encrypted.decode()

    def decrypt_data(self, encrypted_str):
        decrypted = self.cipher.decrypt(encrypted_str.encode())
        return json.loads(decrypted.decode())

    def hash_block(self, block):
        encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def add_transaction(self, donor_id, organ_type, hospital, receiver_id):
        data = {
            'donor_id': donor_id,
            'organ_type': organ_type,
            'hospital': hospital,
            'receiver_id': receiver_id
        }

        encrypted_data = self.encrypt_data(data)
        last_block = self.chain[-1]

        block_data = {
            'data_encrypted': encrypted_data,
            'block_hash': self.hash_block(last_block)
        }

        new_block = self.create_block(block_data['block_hash'])
        new_block['data'].append(block_data)
        return new_block

    def get_chain(self, decrypt=False):
        if decrypt:
            for block in self.chain:
                for entry in block['data']:
                    try:
                        entry['data_decrypted'] = self.decrypt_data(entry['data_encrypted'])
                    except Exception:
                        pass
        return self.chain


# Helper to create/load key
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()
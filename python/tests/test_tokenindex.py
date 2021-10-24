# standard imports
import os
import unittest
import json
import logging
import hashlib

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import receipt
from giftable_erc20_token import GiftableToken
from chainlib.eth.tx import unpack
from hexathon import strip_0x
from chainlib.eth.contract import ABIContractEncoder

# local imports
from eth_token_index.index import (
        TokenUniqueSymbolIndex,
        to_identifier,
        )

# test imports
from eth_address_declarator.declarator import Declarator
from eth_address_declarator.unittest import TestAddressDeclaratorBase

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

testdir = os.path.dirname(__file__)


class TestTokenUniqueSymbolIndex(TestAddressDeclaratorBase):

    def setUp(self):
        super(TestTokenUniqueSymbolIndex, self).setUp()
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = TokenUniqueSymbolIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.constructor(self.accounts[0])
        self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        self.token_index_address = r['contract_address']

        (tx_hash_hex, o) = c.add_writer(self.token_index_address, self.accounts[0], self.accounts[0])
        self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)


    def test_register(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = TokenUniqueSymbolIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        
        (tx_hash_hex, o) = c.register(self.token_index_address, self.accounts[0], self.foo_token_address)
        self.rpc.do(o)
        e = unpack(bytes.fromhex(strip_0x(o['params'][0])), self.chain_spec)

        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.address_of(self.token_index_address, 'FOO', sender_address=self.accounts[0])
        r = self.rpc.do(o)
        address = c.parse_address_of(r)
        self.assertEqual(address, strip_0x(self.foo_token_address))
        
        o = c.entry(self.token_index_address, 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        address = c.parse_entry(r)
        self.assertEqual(address, strip_0x(self.foo_token_address))
        
        o = c.entry_count(self.token_index_address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        count = c.parse_entry_count(r)
        self.assertEqual(count, 1)
    

if __name__ == '__main__':
    unittest.main()

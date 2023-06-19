# standard imports
import os
import unittest
import json
import logging
import hashlib

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.address import is_same_address
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import receipt
from chainlib.error import JSONRPCException
from giftable_erc20_token import GiftableToken
from chainlib.eth.tx import unpack
from hexathon import strip_0x
from hexathon import same as same_hex
from chainlib.eth.contract import ABIContractEncoder
from chainlib.eth.unittest.ethtester import EthTesterCase
from eth_accounts_index import AccountsIndex

# local imports
from eth_token_index.index import (
        TokenUniqueSymbolIndex,
        to_identifier,
        )

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

testdir = os.path.dirname(__file__)


class TestTokenUniqueSymbolIndex(EthTesterCase):

    def setUp(self):
        super(TestTokenUniqueSymbolIndex, self).setUp()
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = TokenUniqueSymbolIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.constructor(self.accounts[0])
        self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        self.address = r['contract_address']

        (tx_hash_hex, o) = c.add_writer(self.address, self.accounts[0], self.accounts[0])
        self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        c = GiftableToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.constructor(self.accounts[0], 'FooToken', 'FOO', 6)
        self.rpc.do(o)

        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        self.foo_token_address = r['contract_address']
        logg.debug('foo token published with address {}'.format(self.foo_token_address))


    def test_register(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = TokenUniqueSymbolIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        
        (tx_hash_hex, o) = c.register(self.address, self.accounts[0], self.foo_token_address)
        self.rpc.do(o)
        #e = unpack(bytes.fromhex(strip_0x(o['params'][0])), self.chain_spec)

        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.address_of(self.address, 'FOO', sender_address=self.accounts[0])
        r = self.rpc.do(o)
        address = c.parse_address_of(r)
        self.assertEqual(address, strip_0x(self.foo_token_address))
        
        o = c.entry(self.address, 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        address = c.parse_entry(r)
        self.assertEqual(address, strip_0x(self.foo_token_address))
        
        o = c.entry_count(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        count = c.parse_entry_count(r)
        self.assertEqual(count, 1)


    def test_remove(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = TokenUniqueSymbolIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        
        (tx_hash_hex, o) = c.register(self.address, self.accounts[0], self.foo_token_address)
        self.rpc.do(o)
        #e = unpack(bytes.fromhex(strip_0x(o['params'][0])), self.chain_spec)

        (tx_hash_hex, o) = c.remove(self.address, self.accounts[0], self.foo_token_address)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.address_of(self.address, 'FOO', sender_address=self.accounts[0])
        r = self.rpc.do(o)
        address = c.parse_address_of(r)
        self.assertTrue(is_same_address(address, ZERO_ADDRESS))
        
        o = c.entry(self.address, 0, sender_address=self.accounts[0])
        with self.assertRaises(JSONRPCException):
            self.rpc.do(o)
        
        o = c.entry_count(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        count = c.parse_entry_count(r)
        self.assertEqual(count, 0)

        (tx_hash_hex, o) = c.remove(self.address, self.accounts[0], self.foo_token_address)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)


    def test_identifiers(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = TokenUniqueSymbolIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.register(self.address, self.accounts[0], self.foo_token_address)
        self.rpc.do(o)

        tokens = [
            self.foo_token_address,
                ]
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        token_names = [
                'BAR',
                'BAZ',
                'XYZZY',
                ]
        for token_name in token_names:
            c = GiftableToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
            (tx_hash_hex, o) = c.constructor(self.accounts[0], '{} Token'.format(token_name), token_name, 6)
            self.rpc.do(o)
            o = receipt(tx_hash_hex)
            r = self.rpc.do(o)
            self.assertEqual(r['status'], 1)

            token_address = r['contract_address']

            c = TokenUniqueSymbolIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
            (tx_hash_hex, o) = c.register(self.address, self.accounts[0], token_address)
            self.rpc.do(o)
            o = receipt(tx_hash_hex)
            r = self.rpc.do(o)
            self.assertEqual(r['status'], 1)

            tokens.append(token_address)

        token_names = ['FOO'] + token_names

        i = 0
        for token_name in token_names:
            o = c.address_of(self.address, token_name, sender_address=self.accounts[0])
            r = self.rpc.do(o)
            r = strip_0x(r)
            logg.debug('tokenn {} {} {}'.format(token_name, r, tokens[i]))
            self.assertTrue(same_hex(r[24:], tokens[i]))
            i += 1
 
        o = c.identifier_count(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        self.assertEqual(int(r, 16), 4)

        c = AccountsIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.remove(self.address, self.accounts[0], tokens[1])
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        c = TokenUniqueSymbolIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        o = c.identifier(self.address, 4, sender_address=self.accounts[0])
        with self.assertRaises(Exception):
            self.rpc.do(o)

        o = c.identifier(self.address, 0, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        self.assertEqual(strip_0x(r)[:6], b'FOO'.hex())

        o = c.identifier_count(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        self.assertEqual(int(r, 16), 3)
        
        next_token_test = tokens[2]
        token_names = [
            'FOO',
            'XYZZY',
            'BAZ',
                ]
        tokens = [
            tokens[0],
            tokens[3],
            tokens[2],
                ]
        i = 0
        for token_name in token_names:
            o = c.address_of(self.address, token_name, sender_address=self.accounts[0])
            r = self.rpc.do(o)
            r = strip_0x(r)
            logg.debug('tokenn {} {} {}'.format(token_name, r, tokens[i]))
            self.assertTrue(same_hex(r[24:], tokens[i]))
            i += 1

        c = AccountsIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.remove(self.address, self.accounts[0], next_token_test)
        self.rpc.do(o)
        o = receipt(tx_hash_hex)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        c = TokenUniqueSymbolIndex(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        o = c.identifier(self.address, 1, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        self.assertEqual(strip_0x(r)[:10], b'XYZZY'.hex())

        token_names = [
            'FOO',
            'XYZZY',
                ]
        tokens = [
            tokens[0],
            tokens[1],
                ]
        i = 0
        for token_name in token_names:
            o = c.address_of(self.address, token_name, sender_address=self.accounts[0])
            r = self.rpc.do(o)
            r = strip_0x(r)
            logg.debug('tokenn {} {} {}'.format(token_name, r, tokens[i]))
            self.assertTrue(same_hex(r[24:], tokens[i]))
            i += 1

        o = c.identifier_count(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        self.assertEqual(int(r, 16), 2)





if __name__ == '__main__':
    unittest.main()

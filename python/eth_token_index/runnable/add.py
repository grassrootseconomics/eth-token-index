"""Adds a new token to the token symbol index

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# standard imports
import sys
import os
import json
import argparse
import logging
import hashlib

# external imports
import chainlib.eth.cli
from chainlib.chain import ChainSpec
from chainlib.eth.tx import receipt
from eth_erc20 import ERC20
from chainlib.eth.address import to_checksum_address
from hexathon import add_0x

# local imports
from eth_token_index import TokenUniqueSymbolIndex

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

arg_flags = chainlib.eth.cli.argflag_std_write | chainlib.eth.cli.Flag.EXEC
argparser = chainlib.eth.cli.ArgumentParser(arg_flags)
argparser.add_argument('token_address', type=str, help='Token address to add to index')
args = argparser.parse_args()

extra_args = {
    'token_address': None,
        }
config = chainlib.eth.cli.Config.from_args(args, arg_flags, extra_args=extra_args, default_fee_limit=TokenUniqueSymbolIndex.gas())

wallet = chainlib.eth.cli.Wallet()
wallet.from_config(config)

rpc = chainlib.eth.cli.Rpc(wallet=wallet)
conn = rpc.connect_by_config(config)

chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))


def main():
    signer = rpc.get_signer()
    signer_address = rpc.get_sender_address()

    gas_oracle = rpc.get_gas_oracle()
    nonce_oracle = rpc.get_nonce_oracle()

    c = TokenUniqueSymbolIndex(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)

    token_address = to_checksum_address(config.get('_TOKEN_ADDRESS'))
    if not config.true('_UNSAFE') and token_address != add_0x(config.get('_TOKEN_ADDRESS')):
        raise ValueError('invalid checksum address for token_address')

    contract_address = to_checksum_address(config.get('_EXEC_ADDRESS'))
    if not config.true('_UNSAFE') and contract_address != add_0x(config.get('_EXEC_ADDRESS')):
        raise ValueError('invalid checksum address for contract')

    (tx_hash_hex, o) = c.register(contract_address, signer_address, token_address)

    if config.get('_RPC_SEND'):
        conn.do(o)
        if config.get('_WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
                sys.exit(1)

        c = ERC20(chain_spec)
        o = c.symbol(token_address)
        r = conn.do(o)
        token_symbol = ERC20.parse_symbol(r)

        logg.info('added token {} at {} to token index {}'.format(token_symbol, token_address, contract_address))

        print(tx_hash_hex)
    else:
        print(o)


if __name__ == '__main__':
    main()

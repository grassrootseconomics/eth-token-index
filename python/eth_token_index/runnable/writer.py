"""Adds/removes writers to accounts index

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# standard imports
import os
import json
import argparse
import logging
import sys

# external imports
import chainlib.eth.cli
from chainlib.chain import ChainSpec
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.tx import receipt
from chainlib.eth.address import to_checksum_address
from hexathon import add_0x

# local imports
from eth_token_index.index import TokenUniqueSymbolIndex

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

arg_flags = chainlib.eth.cli.argflag_std_write | chainlib.eth.cli.Flag.EXEC
argparser = chainlib.eth.cli.ArgumentParser(arg_flags)
argparser.add_argument('--rm', action='store_true', help='Delete entry')
argparser.add_positional('address', type=str, help='Update writer array with this address')
args = argparser.parse_args()

extra_args = {
    'rm': None,
    'address': None,
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

    subject_address = to_checksum_address(config.get('_ADDRESS'))
    if not config.true('_UNSAFE') and subject_address != add_0x(config.get('_ADDRESS')):
        raise ValueError('invalid checksum address for subject_address')


    contract_address = to_checksum_address(config.get('_EXEC_ADDRESS'))
    if not config.true('_UNSAFE') and contract_address != add_0x(config.get('_EXEC_ADDRESS')):
        raise ValueError('invalid checksum address for contract')

    if config.get('_RM'):
        (tx_hash_hex, o) = c.delete_writer(contract_address, signer_address, subject_address)
    else:
        (tx_hash_hex, o) = c.add_writer(contract_address, signer_address, subject_address)
    if config.get('_RPC_SEND'):
        conn.do(o)
        if config.get('_WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
                sys.exit(1)

        print(tx_hash_hex)
    else:
        print(o)


if __name__ == '__main__':
    main()

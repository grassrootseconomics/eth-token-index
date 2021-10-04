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
from eth_erc20 import ERC20
from chainlib.eth.address import to_checksum_address
from hexathon import add_0x

# local imports
from eth_token_index import TokenUniqueSymbolIndex

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()
default_format = 'terminal'

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

arg_flags = chainlib.eth.cli.argflag_std_write | chainlib.eth.cli.Flag.EXEC
argparser = chainlib.eth.cli.ArgumentParser(arg_flags)
argparser.add_argument('token_symbol', type=str, nargs='?', help='Token symbol to return address for')
args = argparser.parse_args()

extra_args = {
    'token_symbol': None,
        }
config = chainlib.eth.cli.Config.from_args(args, arg_flags, extra_args=extra_args, default_fee_limit=TokenUniqueSymbolIndex.gas())

#wallet = chainlib.eth.cli.Wallet()
#wallet.from_config(config)

rpc = chainlib.eth.cli.Rpc()
conn = rpc.connect_by_config(config)

chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))


def out_element(e, w=sys.stdout):
    if config.get('_RAW'):
        w.write(e[1] + '\n')
    else:
        w.write(e[1] + '\t' + e[0] + '\n')


def element(ifc, conn, contract_address, token_symbol, w=sys.stdout):
    o = ifc.address_of(contract_address, token_symbol)
    r = conn.do(o)
    a = ifc.parse_address_of(r)
    out_element((token_symbol, a), w)


def ls(ifc, conn, contract_address, token_ifc, w=sys.stdout):
    o = ifc.entry_count(contract_address)
    r = conn.do(o)
    count = ifc.parse_entry_count(r)
    logg.debug('count {}'.format(count))

    for i in range(count):
        o = ifc.entry(contract_address, i)
        r = conn.do(o)
        token_address = ifc.parse_entry(r)

        o = token_ifc.symbol(token_address)
        r = conn.do(o)
        token_symbol = token_ifc.parse_symbol(r)

        element(ifc, conn, contract_address, token_symbol, w)


def main():
    token_ifc = ERC20(chain_spec)
    ifc = TokenUniqueSymbolIndex(chain_spec)

    contract_address = to_checksum_address(config.get('_EXEC_ADDRESS'))
    if not config.true('_UNSAFE') and contract_address != add_0x(config.get('_EXEC_ADDRESS')):
        raise ValueError('invalid checksum address for contract')

    token_symbol = config.get('_TOKEN_SYMBOL')
    if token_symbol != None:
        element(ifc, conn, contract_address, token_symbol, sys.stdout)
    else:
        ls(ifc, conn, contract_address, token_ifc, sys.stdout)


if __name__ == '__main__':
    main()

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
from chainlib.eth.cli.arg import (
        Arg,
        ArgFlag,
        process_args,
        )
from chainlib.eth.cli.config import (
        Config,
        process_config,
        )
from chainlib.eth.cli.log import process_log
from chainlib.eth.settings import process_settings
from chainlib.settings import ChainSettings
from chainlib.eth.address import is_same_address
from chainlib.eth.constant import ZERO_ADDRESS

# local imports
from eth_token_index import TokenUniqueSymbolIndex

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()
default_format = 'terminal'

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_READ | arg_flags.EXEC

argparser = chainlib.eth.cli.ArgumentParser()
argparser.add_argument('token_symbol', type=str, nargs='?', help='Token symbol to return address for')
argparser = process_args(argparser, arg, flags)
args = argparser.parse_args()

logg = process_log(args, logg)

extra_args = {
    'token_symbol': None,
        }
#config = chainlib.eth.cli.Config.from_args(args, arg_flags, extra_args=extra_args, default_fee_limit=TokenUniqueSymbolIndex.gas())
config = Config()
config = process_config(config, arg, args, flags, positional_name='token_symbol')
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


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

        o = ifc.address_of(contract_address, token_symbol)
        r = conn.do(o)
        reverse_token_address = ifc.parse_entry(r)
        logg.debug('checking token idx {} symbol {} address {} reverse address {}'.format(i, token_symbol, token_address, reverse_token_address))
        if is_same_address(token_address, ZERO_ADDRESS):
            logg.warning('token idx {} {} was registered with zero-address'.format(i, token_symbol))
            continue
        if is_same_address(reverse_token_address, ZERO_ADDRESS):
            raise ValueError('token idx {} {} has entry but zero-address reverse lookup. Are you using the correct reverse lookup keys?'.format(i, token_symbol))
        if not is_same_address(token_address, reverse_token_address):
            logg.info('token idx {} {} address {} does not match reverse address {}, skipping'.format(i, token_symbol, token_address, reverse_token_address))
            continue

        element(ifc, conn, contract_address, token_symbol, w)


def main():
    conn = settings.get('CONN')
    token_ifc = ERC20(settings.get('CHAIN_SPEC'))
    ifc = TokenUniqueSymbolIndex(settings.get('CHAIN_SPEC'))

    contract_address = to_checksum_address(config.get('_EXEC_ADDRESS'))
    if not config.true('_UNSAFE') and contract_address != add_0x(config.get('_EXEC_ADDRESS')):
        raise ValueError('invalid checksum address for contract')

    token_symbol = config.get('_POSARG')
    if token_symbol != None:
        element(ifc, conn, contract_address, token_symbol, sys.stdout)
    else:
        ls(ifc, conn, contract_address, token_ifc, sys.stdout)


if __name__ == '__main__':
    main()

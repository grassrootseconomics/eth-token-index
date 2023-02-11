"""Deploys the token symbol index

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# standard imports
import sys
import os
import json
import argparse
import logging

# external imports
import chainlib.eth.cli
from chainlib.chain import ChainSpec
from chainlib.eth.tx import receipt
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

# local imports
from eth_token_index import TokenUniqueSymbolIndex

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE 

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
args = argparser.parse_args()

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags)
#config = process_config_local(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))



#arg_flags = chainlib.eth.cli.argflag_std_write
#argparser = chainlib.eth.cli.ArgumentParser(arg_flags)
#args = argparser.parse_args()
#
#config = chainlib.eth.cli.Config.from_args(args, arg_flags, default_fee_limit=TokenUniqueSymbolIndex.gas())
#
#wallet = chainlib.eth.cli.Wallet()
#wallet.from_config(config)
#
#rpc = chainlib.eth.cli.Rpc(wallet=wallet)
#conn = rpc.connect_by_config(config)
#
#chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))


def main():
    conn = settings.get('CONN')
    c = TokenUniqueSymbolIndex(
            settings.get('CHAIN_SPEC'),
            signer=settings.get('SIGNER'),
            gas_oracle=settings.get('FEE_ORACLE'),
            nonce_oracle=settings.get('NONCE_ORACLE'),
            )
    (tx_hash_hex, o) = c.constructor(
        settings.get('SENDER_ADDRESS')
        )
    if settings.get('RPC_SEND'):
        conn.do(o)
        if config.true('_WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
                sys.exit(1)
            # TODO: pass through translator for keys (evm tester uses underscore instead of camelcase)
            address = r['contractAddress']

            print(address)
        else:
            print(tx_hash_hex)
    else:
        print(o)


if __name__ == '__main__':
    main()

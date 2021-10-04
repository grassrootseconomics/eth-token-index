SOLC = /usr/bin/solc

all: 
	$(SOLC) TokenUniqueSymbolIndex.sol --abi --evm-version byzantium | awk 'NR>3' > TokenUniqueSymbolIndex.json
	$(SOLC) TokenUniqueSymbolIndex.sol --bin --evm-version byzantium | awk 'NR>3' > TokenUniqueSymbolIndex.bin
	truncate -s -1 TokenUniqueSymbolIndex.bin

install: all
	cp -v TokenUniqueSymbolIndex.{json,bin} ../python/eth_token_index/data/
	
.PHONY: install

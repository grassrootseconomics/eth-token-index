SOLC = solc

all: 
	$(SOLC) TokenUniqueSymbolIndex.sol --abi --optimize --evm-version shanghai | awk 'NR>3' > TokenUniqueSymbolIndex.json
	$(SOLC) TokenUniqueSymbolIndex.sol --bin --optimize --evm-version shanghai | awk 'NR>3' > TokenUniqueSymbolIndex.bin
	$(SOLC) TokenUniqueSymbolIndex.sol --metadata --optimize --evm-version shanghai | awk 'NR>3' > TokenUniqueSymbolIndex.metadata.json
	truncate -s -1 TokenUniqueSymbolIndex.bin

install: all
	cp -v *.json ../python/eth_token_index/data/
	cp -v *.bin ../python/eth_token_index/data/
	
.PHONY: install

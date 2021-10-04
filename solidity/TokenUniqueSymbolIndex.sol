pragma solidity >0.6.11;

// SPDX-License-Identifier: GPL-3.0-or-later

contract TokenUniqueSymbolIndex {

	// EIP 173
	address public owner;
	address newOwner;

	mapping ( bytes32 => uint256 ) public registry;
	address[] tokens;

	event OwnershipTransferred(address indexed previousOwner, address indexed newOwner); // EIP173
	event AddressAdded(address indexed addedAccount, uint256 indexed accountIndex); // AccountsIndex

	constructor() public {
		owner = msg.sender;
		tokens.push(address(0));
	}

	// Implements AccountsIndex
	function entry(uint256 _idx) public view returns ( address ) {
		return tokens[_idx + 1];
	}

	// Implements Registry
	function addressOf(bytes32 _key) public view returns ( address ) {
		uint256 idx;

		idx = registry[_key];
		return tokens[idx];
	}

	function register(address _token) public returns (bool) {
		require(msg.sender == owner);

		bytes memory token_symbol;
		bytes32 token_symbol_key;
		uint256 idx;

		(bool _ok, bytes memory _r) = _token.call(abi.encodeWithSignature('symbol()'));
		require(_ok);

		token_symbol = abi.decode(_r, (bytes));
		token_symbol_key = sha256(token_symbol);

		idx = registry[token_symbol_key];
		require(idx == 0);

		registry[token_symbol_key] = tokens.length;
		tokens.push(_token);
		emit AddressAdded(_token, tokens.length - 1);
		return true;
	}

	// Implements AccountsIndex
	function add(address _token) public returns (bool) {
		return register(_token);
	}


	// Implements AccountsIndex
	function entryCount() public view returns ( uint256 ) {
		return tokens.length - 1;
	}

	// Implements EIP173
	function transferOwnership(address _newOwner) public returns (bool) {
		require(msg.sender == owner);
		newOwner = _newOwner;
	}

	// Implements OwnedAccepter
	function acceptOwnership() public returns (bool) {
		address oldOwner;

		require(msg.sender == newOwner);
		oldOwner = owner; 
		owner = newOwner;
		newOwner = address(0);
		emit OwnershipTransferred(oldOwner, owner);
	}


	// Implements EIP165
	function supportsInterface(bytes4 _sum) public pure returns (bool) {
		if (_sum == 0xcbdb05c7) { // AccountsIndex
			return true;
		}
		if (_sum == 0xbb34534c) { // Registry
			return true;
		}
		if (_sum == 0x01ffc9a7) { // EIP165
			return true;
		}
		if (_sum == 0x9493f8b2) { // EIP173
			return true;
		}
		if (_sum == 0x37a47be4) { // OwnedAccepter
			return true;
		}
		return false;
	}
}

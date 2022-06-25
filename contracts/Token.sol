// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/token/ERC721/ERC721.sol";
import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/access/Ownable.sol";

contract Token is ERC721, Ownable {

    constructor(string memory _name, string memory _symbol) ERC721(_name, _symbol) {}

    function mint(address _sender, uint _tokenId)
    external onlyOwner
    {
        _mint(_sender, _tokenId);
    }
}
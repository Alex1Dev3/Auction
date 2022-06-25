### Smart contracts for working of wickrey auction

### Install
    npm install -g ganache-cli@6.12.2  
    pip3 install eth-brownie==1.17.1  
    brownie pm install OpenZeppelin/openzeppelin-contracts@4.5.0 

### Test
    brownie test

### Start
    brownie run example.py
#### _following environment variables are required before starting:_
    export ADMIN_PRIVATE_KEY=XXXXX
    export OWNER_PRIVATE_KEY=XXXXX
    export BETTER1_PRIVATE_KEY=XXXXX
    export BETTER2_PRIVATE_KEY=XXXXX
    export BETTER3_PRIVATE_KEY=XXXXX
#### _it's private keys (values are hidden on XXXXX) for admin auction contracts, owner nft token and betters (who bet on the auction)_

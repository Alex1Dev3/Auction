import pytest
import uuid
import time
from brownie import reverts, web3

PERIOD = 10
TOKENID = 1


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_start(accounts, contract_token, contract_auction):
    admin = accounts[0]
    owner = accounts[1]

    contract_token.mint(owner, TOKENID, {'from': owner})
    contract_token.approve(contract_auction, TOKENID, {'from': owner})
    assert (contract_token.getApproved(TOKENID) == contract_auction) & \
           (contract_token.ownerOf(TOKENID) == owner)
    contract_auction.start(contract_token, TOKENID, PERIOD, {'from': admin})
    assert (contract_token.ownerOf(TOKENID) == contract_auction) & \
           (contract_auction.lotNumber() == 1)


def test_make_bet_errors(accounts, contract_token, contract_auction):
    admin = accounts[0]
    owner = accounts[1]
    better = accounts[2]
    salt = uuid.uuid4().hex
    amount = 1e18

    test_start(accounts, contract_token, contract_auction)
    contract_auction.makeBet(contract_auction.getHash(amount, web3.toHex(text=salt)), {'from': better})
    with reverts("Previous lot is still active"):
        contract_auction.showBet(amount, web3.toHex(text=salt), {'from': better})

    time.sleep(PERIOD)

    contract_auction.showBet(amount, web3.toHex(text=salt), {'from': better})
    contract_auction.calculateLot({'from': admin})

    assert (contract_auction.lots(contract_auction.lotNumber() - 1)[5] == '0x0000000000000000000000000000000000000000') & \
           (contract_token.ownerOf(TOKENID) == owner)


def test_make_bet(accounts, contract_token, contract_auction):
    admin = accounts[0]
    owner = accounts[1]
    better1 = accounts[2]
    better2 = accounts[3]
    amount1 = 1e18
    amount2 = 3e18
    salt1 = uuid.uuid4().hex
    salt2 = uuid.uuid4().hex

    test_start(accounts, contract_token, contract_auction)
    contract_auction.makeBet(contract_auction.getHash(amount1, web3.toHex(text=salt1)), {'from': better1})
    contract_auction.makeBet(contract_auction.getHash(amount2, web3.toHex(text=salt2)), {'from': better2})

    time.sleep(PERIOD)

    contract_auction.showBet(amount1, web3.toHex(text=salt1), {'from': better1})
    contract_auction.showBet(amount2, web3.toHex(text=salt2), {'from': better2})
    contract_auction.calculateLot({'from': admin})

    winnerAddress = contract_auction.lots(contract_auction.lotNumber() - 1)[5]
    winnerAmount = contract_auction.lots(contract_auction.lotNumber() - 1)[6]

    assert (winnerAddress == better2) & (contract_token.ownerOf(TOKENID) == contract_auction)

    balance_owner_prev = owner.balance()
    contract_auction.receiveLot({'value': winnerAmount, 'from': winnerAddress})
    balance_owner_curr = owner.balance()

    assert (balance_owner_prev + winnerAmount == balance_owner_curr) & \
           (contract_token.ownerOf(TOKENID) == winnerAddress)

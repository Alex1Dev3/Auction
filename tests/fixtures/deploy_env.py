import pytest


@pytest.fixture(scope="module")
def contract_auction(accounts, Auction):
    contract = accounts[0].deploy(Auction)
    yield contract


@pytest.fixture(scope="module")
def contract_token(accounts, Token):
    contract = accounts[1].deploy(Token, "Test Token", "TT")
    yield contract

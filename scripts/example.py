import os
import uuid
import time
from brownie import accounts, web3, Auction, Token

PERIOD = 90
TOKENID = 1
ADMIN = accounts.add(os.environ.get('ADMIN_PRIVATE_KEY'))
OWNER = accounts.add(os.environ.get('OWNER_PRIVATE_KEY'))

BETTERS = [
    {
        'account': accounts.add(os.environ.get('BETTER1_PRIVATE_KEY')),
        'amount': 8e18,
        'salt': uuid.uuid4().hex
    },
    {
        'account': accounts.add(os.environ.get('BETTER2_PRIVATE_KEY')),
        'amount': 10e18,
        'salt': uuid.uuid4().hex
    },
    {
        'account': accounts.add(os.environ.get('BETTER3_PRIVATE_KEY')),
        'amount': 7e18,
        'salt': uuid.uuid4().hex
    }
]


def owner(auction, token):
    text = ''
    address = token.ownerOf(TOKENID)
    if address == ADMIN.address:
        text += 'Admin'
    elif address == OWNER.address:
        text += 'Owner'
    elif address == auction.address:
        text += 'Auction contract'
    else:
        text += 'Better' + str(list(filter(lambda item: item[1]['account'].address == address, enumerate(BETTERS)))[0][0] + 1)
    text += ' (' + address + ')'
    return text


def main():
    auction = Auction.deploy({'from': ADMIN})
    token = Token.deploy('Test Token', 'TT', {'from': OWNER})

    token.mint(OWNER, TOKENID, {'from': OWNER})
    token.approve(auction, TOKENID, {'from': OWNER})

    print(f"Addresses:\n Admin: {ADMIN.address}\n Owner: {OWNER.address}\n Auction contract: {auction.address}\n " + '\n '.join(list(map(lambda item: f"Better{item[0] + 1}: {item[1]['account'].address}", enumerate(BETTERS)))))

    print('Begin')
    print(f"Balances:\n Admin: {ADMIN.balance()}\n Owner: {OWNER.balance()}\n Auction contract: {auction.balance()}\n " + '\n '.join(list(map(lambda item: f"Better{item[0]+1}: {item[1]['account'].balance()}", enumerate(BETTERS)))))
    print('Owner NFT: ' + owner(auction, token))

    auction.start(token.address, TOKENID, PERIOD, {'from': ADMIN})

    for i in range(len(BETTERS)):
        auction.makeBet(auction.getHash(BETTERS[i]['amount'], web3.toHex(text=BETTERS[i]['salt'])), {'from': BETTERS[i]['account']})

    time.sleep(PERIOD)

    for i in range(len(BETTERS)):
        auction.showBet(BETTERS[i]['amount'], web3.toHex(text=BETTERS[i]['salt']), {'from': BETTERS[i]['account']})

    auction.calculateLot({'from': ADMIN})

    print('Before receiving')
    print('Owner NFT: ' + owner(auction, token))

    auction.receiveLot({'value': auction.lots(auction.lotNumber() - 1)[6], 'from': auction.lots(auction.lotNumber() - 1)[5]})

    print('End')
    print(f"Balances:\n Admin: {ADMIN.balance()}\n Owner: {OWNER.balance()}\n Auction contract: {auction.balance()}\n " + '\n '.join(list(map(lambda item: f"Better{item[0]+1}: {item[1]['account'].balance()}", enumerate(BETTERS)))))
    print('Owner NFT: ' + owner(auction, token))

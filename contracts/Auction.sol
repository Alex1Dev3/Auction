// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/utils/math/SafeMath.sol";
import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/token/ERC721/IERC721.sol";

contract Auction is Ownable {
    using SafeMath for uint256;

    uint256 public lotNumber;
    struct Lot {
        address tokenAddress;
        uint256 tokenId;
        address ownerAddress;
        uint256 endDate;
        uint256 betNumber;
        address winnerAddress;
        uint256 winnerAmount;
        bool calculated;
        bool received;
    }
    Lot[] public lots;

    struct Bet {
        address better;
        bytes32 hash;
        uint256 amount;
    }
    mapping(uint256 => Bet[]) public lotBets;
    mapping(uint256 => mapping(address => uint256)) public lotBetIndexes;

    modifier onlyCalculated() {
        require(lotNumber == 0 || lots[lotNumber.sub(1)].calculated, "Previous lot is calculated");
        _;
    }

    modifier onlyNotCalculated() {
        require(lotNumber != 0 && !lots[lotNumber.sub(1)].calculated, "Previous lot is not calculated");
        _;
    }

    modifier onlyReceived() {
        require(lotNumber == 0 || lots[lotNumber.sub(1)].received, "Previous lot is received");
        _;
    }

    modifier onlyNotReceived() {
        require(lotNumber != 0 && !lots[lotNumber.sub(1)].received, "Previous lot is not received");
        _;
    }

    modifier onlyActive() {
        require(lotNumber != 0 && lots[lotNumber.sub(1)].endDate > block.timestamp, "Previous lot is still active");
        _;
    }

    modifier onlyNotActive() {
        require(lotNumber == 0 || lots[lotNumber.sub(1)].endDate <= block.timestamp, "Previous lot is still active");
        _;
    }

    function start(address _tokenAddress, uint256 _tokenId, uint256 _period)
    external onlyOwner onlyReceived onlyNotActive
    {
        require(_tokenAddress != address(0), "Empty address");
        require(_period != 0, "Empty period");

        IERC721 token = IERC721(_tokenAddress);
        require(token.getApproved(_tokenId) == address(this), "Token not approved");
        address ownerAddress = token.ownerOf(_tokenId);

        token.transferFrom(ownerAddress, address(this), _tokenId);

        lots.push(Lot({
            tokenAddress: _tokenAddress,
            tokenId: _tokenId,
            ownerAddress: ownerAddress,
            endDate: block.timestamp.add(_period),
            betNumber: 0,
            winnerAddress: address(0),
            winnerAmount: 0,
            calculated: false,
            received: false
        }));
        lotNumber = lotNumber.add(1);
    }

    function makeBet(bytes32 hash)
    external onlyActive
    {
        require(lotBetIndexes[lotNumber.sub(1)][_msgSender()] == 0, "Bet is already made");

        lots[lotNumber.sub(1)].betNumber = lots[lotNumber.sub(1)].betNumber.add(1);
        lotBets[lotNumber.sub(1)].push(Bet({
            better: _msgSender(),
            hash: hash,
            amount: 0
        }));
        lotBetIndexes[lotNumber.sub(1)][_msgSender()] = lots[lotNumber.sub(1)].betNumber;
    }

    function showBet(uint256 amount, bytes32 salt)
    external onlyNotCalculated onlyNotActive
    {
        require(amount != 0, "Empty bet");

        uint256 indexNumber = lotBetIndexes[lotNumber.sub(1)][_msgSender()];
        require(indexNumber != 0, "Bet isn't made");
        require(lotBets[lotNumber.sub(1)][indexNumber.sub(1)].hash == getHash(amount, salt), "Wrong bet data");

        lotBets[lotNumber.sub(1)][indexNumber.sub(1)].amount = amount;
    }

    function calculateLot()
    external onlyOwner onlyNotCalculated onlyNotActive
    {
        Lot storage lot = lots[lotNumber.sub(1)];

        if (lot.betNumber < 2) {
            IERC721(lot.tokenAddress).transferFrom(address(this), lot.ownerAddress, lot.tokenId);
            lot.received = true;
        } else {
            address firstAddress;
            uint256 firstAmount;
            uint256 secondAmount;

            for (uint256 i = 0; i < lot.betNumber; i++) {
                Bet memory bet = lotBets[lotNumber.sub(1)][i];

                if (bet.amount > firstAmount) {
                    secondAmount = firstAmount;
                    firstAmount = bet.amount;
                    firstAddress = bet.better;
                } else if (bet.amount > secondAmount) {
                    secondAmount = bet.amount;
                }
            }

            if (secondAmount == 0) {
                IERC721(lot.tokenAddress).transferFrom(address(this), lot.ownerAddress, lot.tokenId);
                lot.received = true;
            } else {
                lot.winnerAddress = firstAddress;
                lot.winnerAmount = secondAmount;
            }
        }

        lot.calculated = true;
    }

    function receiveLot()
    external payable onlyCalculated onlyNotReceived
    {
        Lot storage lot = lots[lotNumber.sub(1)];

        require(_msgSender() == lot.winnerAddress, "Calling address is not winner");
        require(msg.value >= lot.winnerAmount, "Insufficient funds for receiving");

        address payable to = payable(lot.ownerAddress);

        IERC721(lot.tokenAddress).transferFrom(address(this), _msgSender(), lot.tokenId);
        to.transfer(msg.value);
        lot.received = true;
    }

    function getHash(uint256 amount, bytes32 salt)
    public view
    returns(bytes32)
    {
        return keccak256(abi.encodePacked(amount, salt));
    }
}
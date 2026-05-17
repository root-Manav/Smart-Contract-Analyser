import os

os.makedirs("contracts/vulnerable", exist_ok=True)
os.makedirs("contracts/secure", exist_ok=True)

vulnerable = {

"vuln_reentrancy_1.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy1 {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 bal = balances[msg.sender];
        require(bal > 0, "Nothing to withdraw");
        (bool sent,) = msg.sender.call{value: bal}("");
        require(sent, "Failed");
        balances[msg.sender] = 0;
    }

    receive() external payable {}
}
""",

"vuln_reentrancy_2.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy2 {
    mapping(address => uint256) public credits;

    function donate(address to) public payable {
        credits[to] += msg.value;
    }

    function withdraw(uint256 amount) public {
        require(credits[msg.sender] >= amount, "Insufficient");
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok);
        credits[msg.sender] -= amount;
    }

    receive() external payable {}
}
""",

"vuln_reentrancy_3.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy3 {
    mapping(address => uint256) private balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdrawAll() public {
        uint256 amt = balances[msg.sender];
        require(amt > 0, "Zero balance");
        (bool success,) = payable(msg.sender).call{value: amt}("");
        require(success);
        balances[msg.sender] = 0;
    }

    receive() external payable {}
}
""",

"vuln_reentrancy_4.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy4 {
    mapping(address => uint256) public shares;
    uint256 public totalShares;

    function buy() public payable {
        shares[msg.sender] += msg.value;
        totalShares += msg.value;
    }

    function sell(uint256 amount) public {
        require(shares[msg.sender] >= amount, "Not enough shares");
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok);
        shares[msg.sender] -= amount;
        totalShares -= amount;
    }

    receive() external payable {}
}
""",

"vuln_reentrancy_5.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy5 {
    mapping(address => uint256) public pool;

    function addLiquidity() public payable {
        pool[msg.sender] += msg.value;
    }

    function removeLiquidity(uint256 amount) public {
        require(pool[msg.sender] >= amount);
        (bool sent,) = msg.sender.call{value: amount}("");
        require(sent);
        pool[msg.sender] -= amount;
    }

    receive() external payable {}
}
""",

"vuln_reentrancy_6.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy6 {
    mapping(address => uint256) public stakes;

    function stake() public payable {
        stakes[msg.sender] += msg.value;
    }

    function unstake() public {
        uint256 s = stakes[msg.sender];
        require(s > 0);
        (bool ok,) = payable(msg.sender).call{value: s}("");
        require(ok, "Transfer failed");
        stakes[msg.sender] = 0;
    }

    receive() external payable {}
}
""",

"vuln_reentrancy_7.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnReentrancy7 {
    mapping(address => uint256) public pending;

    function deposit() public payable {
        pending[msg.sender] += msg.value;
    }

    function claim() public {
        uint256 amount = pending[msg.sender];
        require(amount > 0, "Nothing pending");
        (bool success,) = msg.sender.call{value: amount}("");
        require(success);
        pending[msg.sender] = 0;
    }

    receive() external payable {}
}
""",

"vuln_access_1.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess1 {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function changeOwner(address newOwner) public {
        owner = newOwner;
    }

    function withdraw() public {
        require(msg.sender == owner);
        payable(msg.sender).transfer(address(this).balance);
    }

    receive() external payable {}
}
""",

"vuln_access_2.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess2 {
    address public admin;
    mapping(address => uint256) public balances;

    constructor() {
        admin = msg.sender;
    }

    function setAdmin(address a) public {
        admin = a;
    }

    function adminDrain(address payable to) public {
        require(msg.sender == admin);
        to.transfer(address(this).balance);
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    receive() external payable {}
}
""",

"vuln_access_3.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess3 {
    mapping(address => bool) public admins;

    function addAdmin(address a) public {
        admins[a] = true;
    }

    function removeAdmin(address a) public {
        admins[a] = false;
    }

    function adminAction(address payable to, uint256 amt) public {
        require(admins[msg.sender], "Not admin");
        to.transfer(amt);
    }

    receive() external payable {}
}
""",

"vuln_access_4.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess4 {
    address payable public owner;
    uint256 public fee;

    constructor() {
        owner = payable(msg.sender);
        fee = 100;
    }

    function setFee(uint256 f) public {
        fee = f;
    }

    function setOwner(address payable o) public {
        owner = o;
    }

    function collectFees() public {
        require(msg.sender == owner);
        owner.transfer(address(this).balance);
    }

    receive() external payable {}
}
""",

"vuln_access_5.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnAccess5 {
    address public governance;
    uint256 public rewardRate;

    constructor() {
        governance = msg.sender;
        rewardRate = 10;
    }

    function setGovernance(address g) public {
        governance = g;
    }

    function setRewardRate(uint256 r) public {
        rewardRate = r;
    }

    function govWithdraw(address payable to) public {
        require(msg.sender == governance);
        (bool ok,) = to.call{value: address(this).balance}("");
        require(ok);
    }

    receive() external payable {}
}
""",

"vuln_unchecked_1.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked1 {
    function sendReward(address payable to, uint256 amount) public payable {
        to.call{value: amount}("");
    }

    receive() external payable {}
}
""",

"vuln_unchecked_2.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked2 {
    function batchSend(address payable[] memory targets, uint256 amount) public payable {
        for (uint256 i = 0; i < targets.length; i++) {
            targets[i].call{value: amount}("");
        }
    }

    receive() external payable {}
}
""",

"vuln_unchecked_3.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked3 {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function withdraw(address payable to, uint256 amt) public {
        require(msg.sender == owner);
        to.call{value: amt}("");
    }

    receive() external payable {}
}
""",

"vuln_unchecked_4.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked4 {
    mapping(address => uint256) public rewards;

    function setReward(address user, uint256 amt) public {
        rewards[user] = amt;
    }

    function claimReward() public {
        uint256 amt = rewards[msg.sender];
        rewards[msg.sender] = 0;
        payable(msg.sender).call{value: amt}("");
    }

    receive() external payable {}
}
""",

"vuln_unchecked_5.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnUnchecked5 {
    function multiTransfer(
        address payable a,
        address payable b,
        address payable c,
        uint256 amt
    ) public payable {
        a.call{value: amt}("");
        b.call{value: amt}("");
        c.call{value: amt}("");
    }

    receive() external payable {}
}
""",

"vuln_mixed_1.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed1 {
    mapping(address => uint256) public balances;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 bal = balances[msg.sender];
        require(bal > 0);
        (bool ok,) = msg.sender.call{value: bal}("");
        require(ok);
        balances[msg.sender] = 0;
    }

    function ownerWithdraw() public {
        payable(msg.sender).transfer(address(this).balance);
    }

    receive() external payable {}
}
""",

"vuln_mixed_2.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed2 {
    address public admin;
    mapping(address => uint256) public deposits;

    constructor() {
        admin = msg.sender;
    }

    function deposit() public payable {
        deposits[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 amt = deposits[msg.sender];
        require(amt > 0);
        (bool ok,) = payable(msg.sender).call{value: amt}("");
        require(ok);
        deposits[msg.sender] = 0;
    }

    function changeAdmin(address a) public {
        admin = a;
    }

    function adminDrain(address payable to) public {
        require(msg.sender == admin);
        to.call{value: address(this).balance}("");
    }

    receive() external payable {}
}
""",

"vuln_mixed_3.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed3 {
    mapping(address => uint256) public stakes;
    address public governance;

    constructor() {
        governance = msg.sender;
    }

    function stake() public payable {
        stakes[msg.sender] += msg.value;
    }

    function unstake() public {
        uint256 s = stakes[msg.sender];
        require(s > 0);
        (bool ok,) = msg.sender.call{value: s}("");
        require(ok);
        stakes[msg.sender] = 0;
    }

    function setGovernance(address g) public {
        governance = g;
    }

    function govWithdraw(address payable to) public {
        require(msg.sender == governance);
        to.call{value: address(this).balance}("");
    }

    receive() external payable {}
}
""",

"vuln_mixed_4.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed4 {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdrawHalf() public {
        uint256 half = balances[msg.sender] / 2;
        require(half > 0);
        (bool ok,) = msg.sender.call{value: half}("");
        require(ok);
        balances[msg.sender] -= half;
    }

    function sendTo(address payable to, uint256 amt) public {
        to.call{value: amt}("");
    }

    receive() external payable {}
}
""",

"vuln_mixed_5.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VulnMixed5 {
    address public owner;
    mapping(address => uint256) public credits;

    constructor() {
        owner = msg.sender;
    }

    function addCredit(address a, uint256 v) public {
        credits[a] = v;
    }

    function redeemCredit() public {
        uint256 val = credits[msg.sender];
        require(val > 0);
        (bool ok,) = msg.sender.call{value: val}("");
        require(ok);
        credits[msg.sender] = 0;
    }

    function transferOwnership(address o) public {
        owner = o;
    }

    receive() external payable {}
}
""",

}

secure = {

"safe_vault.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeVault {
    mapping(address => uint256) private balances;
    bool private locked;

    modifier noReentrant() {
        require(!locked, "No reentrancy");
        locked = true;
        _;
        locked = false;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amt) public noReentrant {
        require(balances[msg.sender] >= amt, "Insufficient");
        balances[msg.sender] -= amt;
        (bool ok,) = payable(msg.sender).call{value: amt}("");
        require(ok, "Transfer failed");
    }

    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }

    receive() external payable {}
}
""",

"safe_token.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeToken {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(uint256 supply) {
        owner = msg.sender;
        totalSupply = supply;
        balanceOf[msg.sender] = supply;
    }

    function transfer(address to, uint256 amt) public returns (bool) {
        require(to != address(0), "Zero address");
        require(balanceOf[msg.sender] >= amt, "Insufficient");
        balanceOf[msg.sender] -= amt;
        balanceOf[to] += amt;
        return true;
    }

    function mint(uint256 amt) public onlyOwner {
        totalSupply += amt;
        balanceOf[owner] += amt;
    }
}
""",

"safe_voting.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeVoting {
    address public owner;
    mapping(address => bool) public hasVoted;
    mapping(uint256 => uint256) public votes;
    bool public active;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier isActive() {
        require(active, "Voting closed");
        _;
    }

    constructor() {
        owner = msg.sender;
        active = true;
    }

    function vote(uint256 id) public isActive {
        require(!hasVoted[msg.sender], "Already voted");
        hasVoted[msg.sender] = true;
        votes[id]++;
    }

    function close() public onlyOwner {
        active = false;
    }
}
""",

"safe_escrow.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeEscrow {
    address public buyer;
    address public seller;
    address public arbiter;
    uint256 public amount;
    bool public released;
    bool public refunded;

    modifier onlyArbiter() {
        require(msg.sender == arbiter, "Not arbiter");
        _;
    }

    constructor(address _seller, address _arbiter) payable {
        buyer   = msg.sender;
        seller  = _seller;
        arbiter = _arbiter;
        amount  = msg.value;
    }

    function release() public onlyArbiter {
        require(!released && !refunded, "Already settled");
        released = true;
        (bool ok,) = seller.call{value: amount}("");
        require(ok, "Transfer failed");
    }

    function refund() public onlyArbiter {
        require(!released && !refunded, "Already settled");
        refunded = true;
        (bool ok,) = buyer.call{value: amount}("");
        require(ok, "Transfer failed");
    }
}
""",

"safe_auction.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeAuction {
    address public owner;
    address public topBidder;
    uint256 public topBid;
    bool public ended;
    mapping(address => uint256) public pending;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function bid() public payable {
        require(!ended, "Auction ended");
        require(msg.value > topBid, "Bid too low");
        if (topBidder != address(0)) {
            pending[topBidder] += topBid;
        }
        topBidder = msg.sender;
        topBid    = msg.value;
    }

    function withdraw() public {
        uint256 amt = pending[msg.sender];
        require(amt > 0, "Nothing to withdraw");
        pending[msg.sender] = 0;
        (bool ok,) = payable(msg.sender).call{value: amt}("");
        require(ok, "Transfer failed");
    }

    function endAuction() public onlyOwner {
        require(!ended, "Already ended");
        ended = true;
        (bool ok,) = owner.call{value: topBid}("");
        require(ok, "Transfer failed");
    }
}
""",

"safe_staking.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeStaking {
    mapping(address => uint256) public staked;
    mapping(address => uint256) public since;
    uint256 public rate = 5;

    function stake() public payable {
        require(msg.value > 0, "Must stake ETH");
        staked[msg.sender] += msg.value;
        since[msg.sender]   = block.timestamp;
    }

    function unstake() public {
        uint256 s = staked[msg.sender];
        require(s > 0, "Nothing staked");
        uint256 dur    = block.timestamp - since[msg.sender];
        uint256 reward = (s * rate * dur) / (365 days * 100);
        staked[msg.sender] = 0;
        since[msg.sender]  = 0;
        (bool ok,) = payable(msg.sender).call{value: s + reward}("");
        require(ok, "Transfer failed");
    }
}
""",

"safe_multisig.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeMultiSig {
    address[] public owners;
    uint256 public required;
    mapping(address => bool) public isOwner;

    struct Tx {
        address to;
        uint256 value;
        bool    done;
        uint256 confirms;
    }

    Tx[] public txs;
    mapping(uint256 => mapping(address => bool)) public confirmed;

    modifier onlyOwner() {
        require(isOwner[msg.sender], "Not owner");
        _;
    }

    constructor(address[] memory _owners, uint256 _req) {
        require(_owners.length >= _req, "Invalid required");
        required = _req;
        for (uint256 i = 0; i < _owners.length; i++) {
            isOwner[_owners[i]] = true;
            owners.push(_owners[i]);
        }
    }

    function submit(address to, uint256 val) public onlyOwner returns (uint256) {
        txs.push(Tx(to, val, false, 0));
        return txs.length - 1;
    }

    function confirm(uint256 id) public onlyOwner {
        require(!confirmed[id][msg.sender], "Already confirmed");
        confirmed[id][msg.sender] = true;
        txs[id].confirms++;
    }

    function execute(uint256 id) public onlyOwner {
        Tx storage t = txs[id];
        require(t.confirms >= required, "Not enough confirms");
        require(!t.done, "Already executed");
        t.done = true;
        (bool ok,) = t.to.call{value: t.value}("");
        require(ok, "Execution failed");
    }

    receive() external payable {}
}
""",

"safe_registry.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeRegistry {
    address public owner;
    mapping(string => address) private reg;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function register(string memory name, address addr) public onlyOwner {
        require(addr != address(0), "Zero address");
        require(reg[name] == address(0), "Name taken");
        reg[name] = addr;
    }

    function resolve(string memory name) public view returns (address) {
        return reg[name];
    }
}
""",

"safe_timelock.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeTimelock {
    address public owner;
    uint256 public delay;
    mapping(bytes32 => uint256) public queued;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(uint256 _delay) {
        owner = msg.sender;
        delay = _delay;
    }

    function queue(bytes32 id) public onlyOwner {
        queued[id] = block.timestamp + delay;
    }

    function execute(
        bytes32 id,
        address target,
        uint256 value,
        bytes memory data
    ) public onlyOwner {
        require(queued[id] != 0, "Not queued");
        require(block.timestamp >= queued[id], "Too early");
        queued[id] = 0;
        (bool ok,) = target.call{value: value}(data);
        require(ok, "Execution failed");
    }

    receive() external payable {}
}
""",

"safe_dao.sol": """\
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeDAO {
    struct Proposal {
        string   desc;
        uint256  yes;
        uint256  no;
        bool     executed;
        uint256  deadline;
    }

    Proposal[] public proposals;
    mapping(address => uint256) public tokens;
    address public admin;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function giveTokens(address a, uint256 amt) public onlyAdmin {
        tokens[a] = amt;
    }

    function propose(string memory desc, uint256 duration) public returns (uint256) {
        proposals.push(Proposal(desc, 0, 0, false, block.timestamp + duration));
        return proposals.length - 1;
    }

    function vote(uint256 id, bool support) public {
        Proposal storage p = proposals[id];
        require(block.timestamp < p.deadline, "Voting ended");
        require(tokens[msg.sender] > 0, "No tokens");
        if (support) p.yes += tokens[msg.sender];
        else         p.no  += tokens[msg.sender];
    }
}
""",

}

print("Writing vulnerable contracts...")
for name, code in vulnerable.items():
    path = os.path.join("contracts", "vulnerable", name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"  OK  {name}")

print(f"\nWriting secure contracts...")
for name, code in secure.items():
    path = os.path.join("contracts", "secure", name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"  OK  {name}")

print(f"\nDone!")
print(f"  Vulnerable : {len(vulnerable)}")
print(f"  Secure     : {len(secure)}")
print(f"\nNext steps:")
print(f"  python extract_features.py")
print(f"  python train_model.py")
print(f"  streamlit run app.py")
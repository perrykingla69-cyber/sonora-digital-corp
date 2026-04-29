// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * MDXPoints — ABE Academy utility token (ERC-20)
 * Anti-speculation: transfers only between verified wallets.
 * Legal: NOT a security. Educational loyalty points only.
 */
contract MDXPoints is ERC20, Ownable, Pausable {
    string public constant LEGAL_DISCLAIMER = "Este token NO es un valor mobiliario segun la Ley del Mercado de Valores de Mexico. Es un punto de lealtad educativo sin valor de cambio garantizado.";

    mapping(address => bool) public verifiedWallets;
    mapping(address => bool) public minters;

    event WalletVerified(address indexed wallet);
    event WalletRevoked(address indexed wallet);
    event MinterAdded(address indexed minter);
    event PointsAwarded(address indexed student, uint256 amount, string reason);

    modifier onlyMinter() {
        require(minters[msg.sender] || msg.sender == owner(), "Not a minter");
        _;
    }

    constructor() ERC20("MDX Points", "MDX") Ownable(msg.sender) {}

    function verifyWallet(address wallet) external onlyOwner {
        verifiedWallets[wallet] = true;
        emit WalletVerified(wallet);
    }

    function revokeWallet(address wallet) external onlyOwner {
        verifiedWallets[wallet] = false;
        emit WalletRevoked(wallet);
    }

    function addMinter(address minter) external onlyOwner {
        minters[minter] = true;
        emit MinterAdded(minter);
    }

    function awardPoints(address student, uint256 amount, string calldata reason) external onlyMinter whenNotPaused {
        require(verifiedWallets[student], "Student wallet not verified");
        _mint(student, amount * 10 ** decimals());
        emit PointsAwarded(student, amount, reason);
    }

    function transfer(address to, uint256 amount) public override whenNotPaused returns (bool) {
        require(verifiedWallets[msg.sender] && verifiedWallets[to], "Both wallets must be verified");
        return super.transfer(to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) public override whenNotPaused returns (bool) {
        require(verifiedWallets[from] && verifiedWallets[to], "Both wallets must be verified");
        return super.transferFrom(from, to, amount);
    }

    function pause() external onlyOwner { _pause(); }
    function unpause() external onlyOwner { _unpause(); }

    function decimals() public pure override returns (uint8) { return 2; }
}

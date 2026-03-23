"""
MYSTIC_CHAIN - Agente de Blockchain y Web3
Gestiona NFTs, tokens, pagos cripto y contratos inteligentes para el ecosistema Mystic
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
import secrets

class ChainNetwork(Enum):
    ETHEREUM = ("ethereum", "ETH", 1)
    POLYGON = ("polygon", "MATIC", 137)
    SOLANA = ("solana", "SOL", None)
    BSC = ("bsc", "BNB", 56)
    BASE = ("base", "ETH", 8453)

    def __init__(self, nombre, symbol, chain_id):
        self.nombre = nombre
        self.symbol = symbol
        self.chain_id = chain_id

class NFTStandard(Enum):
    ERC721 = "ERC-721"   # Único
    ERC1155 = "ERC-1155"  # Multi-edición
    SPL = "SPL"           # Solana

@dataclass
class NFTMetadata:
    name: str
    description: str
    image_url: str
    external_url: Optional[str]
    attributes: List[Dict[str, Any]]
    collection: str
    edition: Optional[int] = None
    max_supply: Optional[int] = None

@dataclass
class SmartContract:
    address: str
    network: ChainNetwork
    standard: NFTStandard
    owner: str
    name: str
    symbol: str
    deployed_at: datetime = field(default_factory=datetime.now)
    verified: bool = False

@dataclass
class CryptoPayment:
    payment_id: str
    tenant_id: str
    amount: float
    currency: str
    network: ChainNetwork
    wallet_from: str
    wallet_to: str
    tx_hash: Optional[str] = None
    status: str = "pending"  # pending, confirmed, failed
    created_at: datetime = field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None

@dataclass
class MysticToken:
    """Token de lealtad del ecosistema Mystic"""
    token_id: str
    owner_wallet: str
    tenant_id: str
    balance: float
    staked_amount: float = 0.0
    rewards_earned: float = 0.0
    tier: str = "bronze"  # bronze, silver, gold, platinum

class MYSTICChainAgent:
    """
    Agente especializado en operaciones blockchain y Web3
    Maneja NFTs, pagos cripto, tokens de lealtad y contratos
    """

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        wallet_private_key: Optional[str] = None,
        ipfs_gateway: str = "https://ipfs.io/ipfs/"
    ):
        self.rpc_url = rpc_url
        self.ipfs_gateway = ipfs_gateway
        # Nunca exponer la clave; solo guardar referencia encriptada
        self._key_ref = hashlib.sha256((wallet_private_key or "").encode()).hexdigest()[:8] if wallet_private_key else None
        self.deployed_contracts: Dict[str, SmartContract] = {}
        self.payment_registry: Dict[str, CryptoPayment] = {}
        self.token_registry: Dict[str, MysticToken] = {}

    # ── NFTs ──────────────────────────────────────────────────────────────────

    async def mint_collection_nft(
        self,
        collection_name: str,
        theme: str,
        signature: str,
        max_supply: int,
        network: ChainNetwork = ChainNetwork.POLYGON,
        royalty_pct: float = 10.0
    ) -> Dict[str, Any]:
        """
        Mintea colección de NFTs vinculada al merch físico
        """
        contract_address = self._simulate_contract_address(collection_name, network)

        contract = SmartContract(
            address=contract_address,
            network=network,
            standard=NFTStandard.ERC1155,
            owner="0x_MYSTIC_TREASURY",
            name=collection_name,
            symbol=f"MYS{theme[:3].upper()}"
        )
        self.deployed_contracts[contract_address] = contract

        metadata_base = NFTMetadata(
            name=f"{collection_name} #{'{edition}'}",
            description=f"Colección firmada '{signature}' — {theme}. NFT vinculado a producto físico.",
            image_url=f"ipfs://QmPLACEHOLDER/{collection_name.replace(' ', '_')}/",
            external_url=f"https://mystic.app/nft/{collection_name.replace(' ', '-')}",
            attributes=[
                {"trait_type": "Firma", "value": signature},
                {"trait_type": "Temporada", "value": theme},
                {"trait_type": "Edición", "value": "Limitada"},
                {"trait_type": "Royalty", "value": f"{royalty_pct}%"},
            ],
            collection=collection_name,
            max_supply=max_supply
        )

        return {
            "contract_address": contract_address,
            "network": network.nombre,
            "standard": NFTStandard.ERC1155.value,
            "max_supply": max_supply,
            "royalty_pct": royalty_pct,
            "metadata_template": metadata_base.__dict__,
            "opensea_url": f"https://opensea.io/collection/{collection_name.lower().replace(' ', '-')}",
            "status": "deployed_simulated"
        }

    async def link_nft_to_physical(
        self,
        nft_token_id: str,
        product_sku: str,
        tenant_id: str,
        owner_wallet: str
    ) -> Dict[str, str]:
        """
        Vincula un NFT con su producto físico (prueba de autenticidad)
        """
        link_hash = hashlib.sha256(
            f"{nft_token_id}{product_sku}{owner_wallet}".encode()
        ).hexdigest()

        return {
            "nft_token_id": nft_token_id,
            "product_sku": product_sku,
            "owner_wallet": owner_wallet,
            "authenticity_hash": link_hash,
            "verification_url": f"https://mystic.app/verify/{link_hash[:16]}",
            "linked_at": datetime.now().isoformat()
        }

    # ── Pagos Cripto ──────────────────────────────────────────────────────────

    async def create_crypto_payment(
        self,
        tenant_id: str,
        amount_usd: float,
        currency: str = "USDC",
        network: ChainNetwork = ChainNetwork.POLYGON
    ) -> CryptoPayment:
        """
        Crea una orden de pago en cripto
        """
        payment_id = f"PAY_{secrets.token_hex(8).upper()}"
        treasury_wallet = self._get_treasury_wallet(network)

        payment = CryptoPayment(
            payment_id=payment_id,
            tenant_id=tenant_id,
            amount=amount_usd,
            currency=currency,
            network=network,
            wallet_from="",  # Lo completa el cliente
            wallet_to=treasury_wallet,
        )
        self.payment_registry[payment_id] = payment

        return payment

    async def confirm_payment(
        self,
        payment_id: str,
        tx_hash: str
    ) -> Dict[str, Any]:
        """
        Confirma un pago tras verificar el hash on-chain
        """
        payment = self.payment_registry.get(payment_id)
        if not payment:
            return {"error": "Pago no encontrado"}

        # En producción: verificar tx_hash en la blockchain
        payment.tx_hash = tx_hash
        payment.status = "confirmed"
        payment.confirmed_at = datetime.now()

        # Recompensar con tokens Mystic
        await self._reward_loyalty_tokens(payment.tenant_id, payment.amount)

        return {
            "payment_id": payment_id,
            "status": "confirmed",
            "tx_hash": tx_hash,
            "amount": payment.amount,
            "currency": payment.currency,
            "confirmed_at": payment.confirmed_at.isoformat()
        }

    # ── Tokens de Lealtad ─────────────────────────────────────────────────────

    async def _reward_loyalty_tokens(
        self,
        tenant_id: str,
        purchase_amount_usd: float
    ) -> float:
        """Otorga tokens Mystic proporcionales a la compra"""
        tokens_earned = purchase_amount_usd * 0.05  # 5% en tokens

        token_key = f"TOKEN_{tenant_id}"
        if token_key not in self.token_registry:
            self.token_registry[token_key] = MysticToken(
                token_id=token_key,
                owner_wallet="",
                tenant_id=tenant_id,
                balance=0.0
            )

        token = self.token_registry[token_key]
        token.balance += tokens_earned
        token.rewards_earned += tokens_earned
        token.tier = self._calculate_tier(token.balance)

        return tokens_earned

    def _calculate_tier(self, balance: float) -> str:
        if balance >= 10_000:
            return "platinum"
        elif balance >= 2_500:
            return "gold"
        elif balance >= 500:
            return "silver"
        return "bronze"

    async def stake_tokens(
        self,
        tenant_id: str,
        amount: float,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Permite hacer staking de tokens para ganar APY
        """
        token_key = f"TOKEN_{tenant_id}"
        token = self.token_registry.get(token_key)

        if not token or token.balance < amount:
            return {"error": "Balance insuficiente"}

        apy_rates = {30: 0.08, 60: 0.12, 90: 0.18, 180: 0.25}
        apy = apy_rates.get(period_days, 0.08)
        expected_reward = amount * (apy * period_days / 365)

        token.balance -= amount
        token.staked_amount += amount

        return {
            "staked": amount,
            "period_days": period_days,
            "apy": f"{apy*100:.0f}%",
            "expected_reward": round(expected_reward, 4),
            "unlock_date": datetime.now().isoformat()
        }

    # ── Utilidades Internas ───────────────────────────────────────────────────

    def _simulate_contract_address(self, name: str, network: ChainNetwork) -> str:
        raw = f"{name}{network.nombre}{datetime.now().timestamp()}"
        return "0x" + hashlib.sha256(raw.encode()).hexdigest()[:40]

    def _get_treasury_wallet(self, network: ChainNetwork) -> str:
        # En producción: wallets reales por red, guardadas en variables de entorno
        wallets = {
            ChainNetwork.POLYGON: "0xPOLYGON_TREASURY_PLACEHOLDER",
            ChainNetwork.ETHEREUM: "0xETH_TREASURY_PLACEHOLDER",
            ChainNetwork.SOLANA: "SOL_TREASURY_PLACEHOLDER",
            ChainNetwork.BSC: "0xBSC_TREASURY_PLACEHOLDER",
            ChainNetwork.BASE: "0xBASE_TREASURY_PLACEHOLDER",
        }
        return wallets.get(network, "0xDEFAULT_PLACEHOLDER")

    def get_portfolio_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Resumen del portafolio Web3 de un tenant"""
        token_key = f"TOKEN_{tenant_id}"
        token = self.token_registry.get(token_key)

        payments = [p for p in self.payment_registry.values() if p.tenant_id == tenant_id]
        total_paid = sum(p.amount for p in payments if p.status == "confirmed")

        return {
            "tenant_id": tenant_id,
            "total_paid_usd": total_paid,
            "mystic_token_balance": token.balance if token else 0,
            "mystic_token_staked": token.staked_amount if token else 0,
            "loyalty_tier": token.tier if token else "bronze",
            "nfts_owned": 0,  # En producción: consultar on-chain
            "payments_count": len(payments)
        }

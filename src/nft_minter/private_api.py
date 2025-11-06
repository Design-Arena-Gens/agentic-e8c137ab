from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Optional

import httpx
from solders.message import Message
from solders.transaction import VersionedTransaction


@dataclass(frozen=True)
class PrivateApiMintResponse:
    raw_tx: VersionedTransaction


async def request_mint_transaction(
    base_url: str,
    pubkey: str,
    name: str,
    symbol: str,
    uri: str,
    seller_fee_basis_points: int,
    timeout_s: int = 15,
) -> PrivateApiMintResponse:
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        payload = {
            "payer": pubkey,
            "name": name,
            "symbol": symbol,
            "uri": uri,
            "seller_fee_basis_points": seller_fee_basis_points,
        }
        resp = await client.post(f"{base_url.rstrip('/')}/mint", json=payload)
        resp.raise_for_status()
        data = resp.json()
        # Expect { "transaction": "base64-encoded versioned tx" }
        b64_tx = data.get("transaction")
        if not isinstance(b64_tx, str):
            raise RuntimeError("Private API response missing 'transaction' base64 string")
        raw = base64.b64decode(b64_tx)
        tx = VersionedTransaction.from_bytes(raw)
        return PrivateApiMintResponse(raw_tx=tx)

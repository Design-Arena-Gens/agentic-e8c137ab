from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Sequence

from rich.console import Console
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from nft_minter.private_api import request_mint_transaction


console = Console()


@dataclass(frozen=True)
class MintResult:
    payer: Pubkey
    mint: Pubkey
    signature: str


async def build_mint_tx_from_private_api(
    private_api_url: str,
    payer: Keypair,
    name: str,
    symbol: str,
    uri: str,
    seller_fee_basis_points: int,
) -> VersionedTransaction:
    resp = await request_mint_transaction(
        base_url=private_api_url,
        pubkey=str(payer.pubkey()),
        name=name,
        symbol=symbol,
        uri=uri,
        seller_fee_basis_points=seller_fee_basis_points,
    )
    return resp.raw_tx


async def mint_single(
    client: AsyncClient,
    private_api_url: str,
    payer: Keypair,
    name: str,
    symbol: str,
    uri: str,
    seller_fee_basis_points: int,
) -> MintResult:
    vtx = await build_mint_tx_from_private_api(
        private_api_url, payer, name, symbol, uri, seller_fee_basis_points
    )
    # Sign with payer and send
    vtx.sign([payer])
    raw = bytes(vtx)
    resp = await client.send_raw_transaction(raw, opts=TxOpts(skip_preflight=True))
    sig = resp.value
    # Mint pubkey is not decoded here; use default until API returns it
    return MintResult(payer=payer.pubkey(), mint=Pubkey.default(), signature=sig)


async def mint_batch(
    client: AsyncClient,
    private_api_url: str,
    payers: Sequence[Keypair],
    name: str,
    symbol: str,
    uri: str,
    seller_fee_basis_points: int,
    parallelism: int = 4,
) -> list[MintResult]:
    sem = asyncio.Semaphore(parallelism)

    async def _task(kp: Keypair) -> MintResult:
        async with sem:
            return await mint_single(
                client,
                private_api_url,
                kp,
                name,
                symbol,
                uri,
                seller_fee_basis_points,
            )

    return await asyncio.gather(*[_task(kp) for kp in payers])

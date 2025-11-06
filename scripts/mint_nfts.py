#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import sys
from pathlib import Path as _PathForImport
sys.path.append(str((_PathForImport(__file__).resolve().parents[1] / "src").resolve()))
import csv
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from solana.rpc.async_api import AsyncClient

from nft_minter.config import load_config
from nft_minter.wallets import load_wallets
from nft_minter.mint import mint_batch

app = typer.Typer(help="High-performance Solana NFT minter (multi-wallet, private RPC)")
console = Console()


def _load_metadata_from_csv(csv_path: Optional[Path]):
    if not csv_path:
        return None
    rows = []
    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


@app.command()
def mint(
    wallets_paths: list[Path] = typer.Option(
        ..., "--wallet", "-w", help="Wallet keypair JSON files or directories (repeatable)",
    ),
    name: Optional[str] = typer.Option(None, help="NFT name"),
    symbol: Optional[str] = typer.Option(None, help="NFT symbol"),
    uri: Optional[str] = typer.Option(None, help="Metadata URI (Arweave/IPFS/HTTPS)"),
    csv_metadata: Optional[Path] = typer.Option(
        None, "--metadata-csv", help="CSV with columns: name,symbol,uri,seller_fee_basis_points"
    ),
    seller_fee_basis_points: int = typer.Option(500, help="Royalty in basis points, default 500 (5%)"),
    parallelism: int = typer.Option(4, "--parallel", help="Concurrent mints"),
    env_file: Optional[Path] = typer.Option(None, help="Path to .env file (overrides)"),
):
    """Mint NFTs using provided wallets.

    If --metadata-csv is provided, rows are assigned round-robin to wallets.
    Otherwise, a single metadata triple (--name --symbol --uri) is used for all wallets.
    """
    cfg = load_config(str(env_file) if env_file else None)
    if not cfg.private_api_url:
        raise typer.BadParameter("PRIVATE_API_URL must be set in environment or .env file")

    wallets = load_wallets(wallets_paths)

    # Load metadata
    rows = _load_metadata_from_csv(csv_metadata)
    if rows:
        # Validate rows
        for r in rows:
            if not all(k in r and r[k] for k in ("name", "symbol", "uri")):
                raise typer.BadParameter("CSV rows must include name,symbol,uri")
    else:
        if not (name and symbol and uri):
            raise typer.BadParameter("Provide --name, --symbol, and --uri or use --metadata-csv")

    async def _run():
        client = AsyncClient(cfg.rpc_url, commitment=cfg.commitment)
        try:
            results = []
            if rows:
                # Round-robin assign metadata rows to wallets; each wallet mints once.
                assigned = []
                for idx, wallet in enumerate(wallets):
                    row = rows[idx % len(rows)]
                    assigned.append((wallet.keypair, row))

                coros = []
                for kp, row in assigned:
                    coros.append(
                        mint_batch(
                            client=client,
                            private_api_url=cfg.private_api_url,  # type: ignore[arg-type]
                            payers=[kp],
                            name=row["name"],
                            symbol=row["symbol"],
                            uri=row["uri"],
                            seller_fee_basis_points=int(row.get("seller_fee_basis_points", seller_fee_basis_points)),
                            parallelism=1,
                        )
                    )
                batches = await asyncio.gather(*coros)
                for b in batches:
                    results.extend(b)
            else:
                results = await mint_batch(
                    client=client,
                    private_api_url=cfg.private_api_url,  # type: ignore[arg-type]
                    payers=[w.keypair for w in wallets],
                    name=name,  # type: ignore[arg-type]
                    symbol=symbol,  # type: ignore[arg-type]
                    uri=uri,  # type: ignore[arg-type]
                    seller_fee_basis_points=seller_fee_basis_points,
                    parallelism=parallelism,
                )

            table = Table(title="Minted NFTs")
            table.add_column("Payer")
            table.add_column("Mint")
            table.add_column("Signature")
            for r in results:
                table.add_row(str(r.payer), str(r.mint), r.signature)
            console.print(table)
        finally:
            await client.close()

    asyncio.run(_run())


if __name__ == "__main__":
    app()

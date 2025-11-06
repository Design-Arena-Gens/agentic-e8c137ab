from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from solders.keypair import Keypair


@dataclass(frozen=True)
class Wallet:
    name: str
    keypair: Keypair


def load_keypair_from_file(file_path: Path) -> Keypair:
    data = json.loads(file_path.read_text().strip())
    if isinstance(data, list):
        # solana-keygen format
        secret = bytes(data)
        return Keypair.from_bytes(secret)
    elif isinstance(data, dict) and "secret_key" in data:
        # custom format {"secret_key": [..]}
        secret = bytes(data["secret_key"])  # type: ignore[arg-type]
        return Keypair.from_bytes(secret)
    else:
        raise ValueError(f"Unsupported keypair format in {file_path}")


def load_wallets_from_dir(directory: Path) -> List[Wallet]:
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"Wallets directory not found: {directory}")
    wallets: List[Wallet] = []
    for fp in sorted(directory.glob("*.json")):
        kp = load_keypair_from_file(fp)
        wallets.append(Wallet(name=fp.stem, keypair=kp))
    if not wallets:
        raise RuntimeError(f"No wallet keypair JSON files found in {directory}")
    return wallets


def load_wallets(paths: Iterable[Path]) -> List[Wallet]:
    wallets: List[Wallet] = []
    for p in paths:
        if p.is_dir():
            wallets.extend(load_wallets_from_dir(p))
        else:
            kp = load_keypair_from_file(p)
            wallets.append(Wallet(name=p.stem, keypair=kp))
    if not wallets:
        raise RuntimeError("No wallets loaded from given paths")
    return wallets

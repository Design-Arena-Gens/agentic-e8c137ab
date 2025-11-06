from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    rpc_url: str
    commitment: str
    priority_fee_microlamports: Optional[int]
    compute_unit_limit: Optional[int]
    private_api_url: Optional[str]


def load_config(env_file: Optional[str] = None) -> AppConfig:
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    rpc_url = os.getenv("PRIVATE_RPC_URL", "")
    if not rpc_url:
        raise RuntimeError(
            "PRIVATE_RPC_URL is required. Provide it via .env or environment variable."
        )

    commitment = os.getenv("COMMITMENT", "finalized")

    priority_fee_raw = os.getenv("PRIORITY_FEE_MICROLAMPORTS")
    priority_fee = int(priority_fee_raw) if priority_fee_raw else None

    compute_unit_limit_raw = os.getenv("COMPUTE_UNIT_LIMIT")
    compute_unit_limit = int(compute_unit_limit_raw) if compute_unit_limit_raw else None

    private_api_url = os.getenv("PRIVATE_API_URL") or None

    return AppConfig(
        rpc_url=rpc_url,
        commitment=commitment,
        priority_fee_microlamports=priority_fee,
        compute_unit_limit=compute_unit_limit,
        private_api_url=private_api_url,
    )

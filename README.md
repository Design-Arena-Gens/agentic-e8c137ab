# Solana NFT Minter (Python CLI)

High-performance Python CLI to mint NFTs on Solana using a private RPC for fast transactions. Supports multiple wallets and concurrent minting. Includes a minimal static site for Vercel deployment.

## 🚀 Features

- Multiple wallets (file and directory support)
- Private RPC support (recommended for speed/reliability)
- Optional priority fee and compute unit tuning
- Concurrency for fast batch minting
- CSV-driven metadata mode or single metadata for all wallets

## 📦 Requirements

- Python 3.10+
- Solana wallet keypairs (JSON, `solana-keygen` format)

## 🔐 Configuration

Create a `.env` based on `.env.example`:

```
PRIVATE_RPC_URL=... # your private RPC
COMMITMENT=finalized
PRIORITY_FEE_MICROLAMPORTS=10000
COMPUTE_UNIT_LIMIT=100000
```

Private/paid RPCs (e.g., Helius, QuickNode, Triton, etc.) are recommended for low-latency, high-throughput transactions.

## 🧰 Setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 👛 Wallets

Place wallet keypair JSON files under `wallets/` or pass file paths explicitly. Supported formats:

- `solana-keygen` JSON array of 64 integers
- `{ "secret_key": [ ... ] }` dictionary

## 🧾 Metadata

You can provide a single metadata triple via CLI or a CSV (`metadata.csv.example` provided) with columns:

```
name,symbol,uri,seller_fee_basis_points
```

## ▶️ Usage

Show help:

```bash
python scripts/mint_nfts.py --help
```

Mint one NFT per wallet with the same metadata:

```bash
python scripts/mint_nfts.py \
  -w wallets \
  --name "Example NFT" \
  --symbol EXN \
  --uri https://arweave.net/example123 \
  --parallel 4
```

Mint using CSV metadata (rows assigned round-robin to wallets):

```bash
python scripts/mint_nfts.py \
  -w wallets \
  --metadata-csv metadata.csv.example \
  --parallel 4
```

Options:

- `--parallel` concurrent transactions (default 4)
- `--metadata-csv` provide per-NFT metadata
- `--name/--symbol/--uri` single metadata for all wallets
- `--env-file` custom .env path

## 📁 Project Structure

```
├── scripts/
│   └── mint_nfts.py         # CLI entrypoint
├── src/nft_minter/
│   ├── config.py            # Env/config loader
│   ├── wallets.py           # Wallet loading utilities
│   └── mint.py              # Mint logic (Metaplex Token Metadata)
├── wallets/                 # Put your keypair JSONs here
├── metadata.csv.example     # Example CSV metadata
├── .env.example             # Example environment config
├── requirements.txt         # Python deps
├── public/index.html        # Static page for Vercel
└── vercel.json              # Vercel configuration
```

## 🧪 Smoke Test

```bash
. .venv/bin/activate
python scripts/mint_nfts.py --help
```

## 🌐 Deploy Static Site to Vercel

This repo includes a minimal static site (`public/index.html`) so it can be deployed to Vercel.

```bash
vercel deploy --prod --yes --token "$VERCEL_TOKEN" --name agentic-e8c137ab
```

Then verify:

```bash
curl https://agentic-e8c137ab.vercel.app
```

## ⚠️ Notes

- Minting on mainnet costs SOL (rent + fees). Test carefully on devnet first.
- Never commit real private keys. Keep your wallets secure.
- Use a fast private RPC for best performance.

# 🚀 FundFlow - Institutional Crypto Intelligence Platform

**High-fidelity funding intelligence and automated project discovery delivered via a neutral, researcher-grade interface.**

---

## 🏛️ Intelligence Standard
FundFlow is designed for institutional researchers who require cold, factual data over marketing narratives. Every report generated is anchored to verifiable signals and follows a strict **Monochromatic Institutional Standard**.

### 🔍 Unified Discovery Loop
The platform center's around a single command: `/find`.
*   **Local Indexing**: Instantly retrieves project data from our proprietary database.
*   **Real-time discovery**: If a project isn't indexed, the engine launches a global discovery mission across CryptoRank, CoinGecko, and the Deep Web research mesh.
*   **Automatic Ingestion**: Discovered projects are automatically parsed, scored, and added to the permanent index.

### 📑 Intelligence Dossiers (PDF)
Generate 13-section, monochromatic research dossiers on-demand. These reports eliminate subjective grades in favor of direct capital signals, traction metrics, and temporal shifts.
*   **Temporal Intelligence**: Tracks chronological delta-changes in funding, codebase, and positioning.
*   **Gap-Aware Reporting**: Explicitly highlights missing or restricted data in red, ensuring researchers know exactly what is unknown.
*   **Neutral Tone**: Purged of marketing "verdicts"; strictly factual and intent-based.

---

## 📋 Interface Guide

| Command | Action |
| :--- | :--- |
| `/find <name>` | **Primary Hub.** Search, Discover, and Ingest any project. |
| `/latest` | View the last 7-30 days of global funding rounds. |
| `/investor <name>` | Access the institutional portfolio of any fund. |
| `/stats` | Broad market funding statistics and sector breakdowns. |
| `/watch <name>` | Set an intelligence alert to monitor new capital events. |
| `/help` | View detailed methodology and documentation. |

---

## 🛠️ Technology & Architecture

FundFlow's intelligence is powered by a multi-adapter "Data Mesh":
*   **Capital Adapter**: Authoritative funding data via CryptoRank Institutional.
*   **Code Adapter**: Technical health and commit velocity via GitHub Signal.
*   **Usage Adapter**: TVL and revenue tracking via DefiLlama.
*   **Research Mesh**: Deep-web news aggregation and secondary source anchoring.

### Project Structure
```text
fundflow/
├── bot/              # Telegram Interface (Institutional UX)
├── scrapers/         # Data Mesh Adapters (CryptoRank, Web, etc.)
├── utils/            # Intelligence Synthesis & PDF Generation
├── database/         # Factual Substrate (PostgreSQL)
└── config/           # System Constants & Credentials
```

---

## 🚀 Deployment

### Prerequisites
- Python 3.11+
- PostgreSQL & Redis
- Telegram Bot Token

### Installation
```bash
# 1. Clone & Install
git clone [repository-url]
cd fundflow
pip install -r requirements.txt

# 2. Configure Environment
cp config/.env.example config/.env
# Populate with local database URLs and API keys

# 3. Initialize & Start
python -m database.init_db
./scripts/run_bot.sh
```

### Automatic Reliability
The platform includes a built-in supervisor script (`scripts/run_bot.sh`) that ensures the bot automatically restarts in the event of a network or API failure. For production environments, a `systemd` unit file is provided in `deploy/`.

---

## 🏛️ Disclaimer
FundFlow provides raw intelligence substrate. All data is synthesized from public signals and is intended for institutional research purposes only. "Confidence" scores refer to the integrity of the data collection process, not the success of the project.

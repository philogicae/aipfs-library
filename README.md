# aipfs-library

Decentralized media library managed by AI agents indexing torrents and curated by the community

## Requirements

### Tools

- **Backend (Agent)**:
    - `docker`
    - `python v3.12.x` ([pyenv](https://github.com/pyenv/pyenv#installation) recommended)

- **Frontent (Dapp)**:
    - `nodejs v22` ([nvm](https://github.com/nvm-sh/nvm#installing-and-updating) recommended)
    - `pnpm v9.x.x`
    - *Optional:* add [biomejs](https://biomejs.dev/guides/editors/first-party-extensions/) to IDE

### Configuration

- **Backend (Agent)**:
    - Copy `.env.example` to `.env` file and update it

- **Frontent (Dapp)**:
    - Copy `.env.example` to `.env` file and update it

## Installation

- **Backend (Agent)**:
```bash
cd agent
./1_install-env.sh
```

- **Frontent (Dapp)**:
```bash
cd dapp
pnpm install
```

## Scripts

- **Backend (Agent)**:
```bash	
./scripts/2_test-agent.sh
./scripts/3_deploy-agent.sh
./scripts/4_logs-agent.sh
```

- **Frontent (Dapp)**:
```bash	
pnpm run dev
pnpm run build
```
"""production/05_deployment: Systemd/container deployment configuration.

Generates systemd service files, Docker Compose, and environment configuration
for production deployment of Vyapaar strategies.

Run::

    python examples/production/05_deployment.py --output /etc/vyapaar/
    python examples/production/05_deployment.py  # prints to stdout

Pitfalls::

    - The generated unit and Dockerfile run `python -m vyapaar.session.run`, which does not exist in
      the vyapaar package (session is a single module). Under Restart=on-failure the service would
      restart every 10 seconds without ever trading. Treat the files as a template and set a real
      entry point.
    - Secrets: .env.template has blank DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN. The real .env must be
      mode 600, owned by the service user and never committed. `COPY . .` bakes it into the image
      unless .dockerignore excludes it, and EnvironmentFile=- means a missing file is silently
      ignored, so the service can start without credentials.
    - Config drift: capital and risk limits appear in both the .env and the TOML with nothing saying
      which wins. The unit reads {workdir}/config but the script writes under --output, so they
      agree only when those match. The base image is python:3.11-slim with an unpinned
      requirements.txt and an image tagged :latest, so a redeploy can change behaviour.
    - Restarts and shutdown: only the default SIGTERM is configured, with no ExecStop or timeout to
      cancel open orders. A restart mid-session must reconcile with the broker, and containers
      default to UTC, so set TZ or use IST-aware times and add a market-hours guard. strategy_name
      is validated, since it becomes file names.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from vyapaar_examples.cli import add_out_arg, emit_json, make_parser

__all__ = ["main", "run"]

_STRATEGY_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")


SYSTEMD_SERVICE = """[Unit]
Description=Vyapaar Trading Strategy: {strategy_name}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User={user}
Group={group}
WorkingDirectory={workdir}
Environment=PYTHONPATH={workdir}
Environment=VYAAPAAR_STRATEGIES_DIR={strategies_dir}
EnvironmentFile=-{env_file}
ExecStart={python} -m vyapaar.session.run --config {config_file}
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vyapaar-{strategy_name}

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={workdir}/logs {workdir}/data

[Install]
WantedBy=multi-user.target
"""

DOCKER_COMPOSE = """version: '3.8'

services:
  vyapaar-{strategy_name}:
    image: vyapaar/{strategy_name}:latest
    build:
      context: .
      dockerfile: Dockerfile
    container_name: vyapaar-{strategy_name}
    restart: unless-stopped
    environment:
      - PYTHONPATH=/app
      - VYAAPAAR_STRATEGIES_DIR=/app/strategies
    env_file:
      - .env
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - vyapaar-net
    deploy:
      resources:
        limits:
          cpus: '1'
        reservations:
          cpus: '0.5'
          memory: 512M

networks:
  vyapaar-net:
    driver: bridge
"""

DOCKERFILE = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Vyapaar and dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Non-root user
RUN useradd -m -u 1000 vyapaar && chown -R vyapaar:vyapaar /app
USER vyapaar

CMD ["python", "-m", "vyapaar.session.run", "--config", "config/{strategy_name}.toml"]
"""

ENV_TEMPLATE = """# Vyapaar Production Environment
# Copy to .env and fill in values

# Adapter credentials
DHAN_CLIENT_ID=
DHAN_ACCESS_TOKEN=

# Strategy config
STRATEGY_NAME=sma_crossover
SYMBOL=RELIANCE
EXCHANGE=NSE
TIMEFRAME=1d
CAPITAL=100000
FAST_PERIOD=10
SLOW_PERIOD=30

# Risk limits
MAX_POSITION_PCT=0.1
MAX_DAILY_LOSS=50000
MAX_DRAWDOWN_PCT=0.15

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/vyapaar.log

# Monitoring
METRICS_PORT=9090
HEALTH_PORT=9091
"""


def run(
    strategy_name: str = "sma_crossover",
    output: Path | None = None,
    user: str = "vyapaar",
    group: str = "vyapaar",
    workdir: str = "/opt/vyapaar",
    strategies_dir: str = "/opt/vyapaar/strategies",
    python: str = "/usr/bin/python3",
) -> dict[str, Any]:
    if not _STRATEGY_NAME.fullmatch(strategy_name) or ".." in strategy_name:
        raise ValueError(
            f"invalid strategy name {strategy_name!r}: use letters, digits, '_', '-' and '.' only"
        )
    config = {
        "strategy_name": strategy_name,
        "user": user,
        "group": group,
        "workdir": workdir,
        "strategies_dir": strategies_dir,
        "python": python,
        "env_file": f"{workdir}/.env",
        "config_file": f"{workdir}/config/{strategy_name}.toml",
    }

    systemd = SYSTEMD_SERVICE.format(**config)
    docker_compose = DOCKER_COMPOSE.format(strategy_name=strategy_name)
    dockerfile = DOCKERFILE.format(strategy_name=strategy_name)
    env = ENV_TEMPLATE

    if output:
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)

        # Systemd
        (output / f"vyapaar-{strategy_name}.service").write_text(systemd)

        # Docker
        (output / "docker-compose.yml").write_text(docker_compose)
        (output / "Dockerfile").write_text(dockerfile)

        # Env template
        (output / ".env.template").write_text(env)

        # Config directory
        (output / "config").mkdir(exist_ok=True)
        config_toml = f"""# {strategy_name} production config
[strategy]
name = "{strategy_name}"
symbol = "RELIANCE"
exchange = "NSE"
timeframe = "1d"
capital = 100000
fast_period = 10
slow_period = 30

[risk]
max_position_pct = 0.1
max_daily_loss = 50000
max_drawdown_pct = 0.15

[adapter]
name = "dhan"
# client_id and access_token from .env

[session]
log_level = "INFO"
metrics_port = 9090
"""
        (output / f"config/{strategy_name}.toml").write_text(config_toml)

        return {
            "status": "written",
            "output_dir": str(output),
            "files": [
                f"vyapaar-{strategy_name}.service",
                "docker-compose.yml",
                "Dockerfile",
                ".env.template",
                f"config/{strategy_name}.toml",
            ],
        }

    return {
        "status": "stdout",
        "systemd_service": systemd,
        "docker_compose": docker_compose,
        "dockerfile": dockerfile,
        "env_template": env,
    }


def main(argv: list[str] | None = None) -> int:
    parser = make_parser(__doc__)
    parser.add_argument("--strategy", type=str, default="sma_crossover")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--user", type=str, default="vyapaar")
    parser.add_argument("--group", type=str, default="vyapaar")
    parser.add_argument("--workdir", type=str, default="/opt/vyapaar")
    parser.add_argument("--strategies-dir", type=str, default="/opt/vyapaar/strategies")
    parser.add_argument("--python", type=str, default="/usr/bin/python3")
    add_out_arg(parser)
    args = parser.parse_args(argv)

    result = run(
        strategy_name=args.strategy,
        output=args.output,
        user=args.user,
        group=args.group,
        workdir=args.workdir,
        strategies_dir=args.strategies_dir,
        python=args.python,
    )

    if args.out:
        emit_json(result, args.out)
    elif args.output is None:
        print("=== Systemd Service ===")
        print(result["systemd_service"])
        print("\n=== Docker Compose ===")
        print(result["docker_compose"])
        print("\n=== Dockerfile ===")
        print(result["dockerfile"])
        print("\n=== Environment Template ===")
        print(result["env_template"])

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Configuration loader for YAML-based backtest configurations.

This module provides utilities for loading and validating backtest
configurations from YAML files.
"""

import yaml
from pathlib import Path
from typing import Any, Dict


class BacktestConfig:
    """Container for backtest configuration loaded from YAML."""

    def __init__(self, config_dict: Dict[str, Any]):
        self.raw = config_dict
        self.name = config_dict.get("name", "Unnamed Backtest")
        self.description = config_dict.get("description", "")

        # Tickers
        self.tickers = config_dict.get("tickers", [])

        # Strategies
        self.strategies = config_dict.get("strategies", [])
        self.portfolio_strategies = config_dict.get("portfolio_strategies", [])

        # Periods
        periods_config = config_dict.get("periods", {})
        self.lookback_days = periods_config.get("lookback_days", [])
        self.full_sample = periods_config.get("full_sample", True)
        self.market_regimes = periods_config.get("market_regimes", [])

        # Rolling windows
        rolling_config = config_dict.get("rolling_windows", {})
        self.rolling_enabled = rolling_config.get("enabled", False)
        self.rolling_window = rolling_config.get("window", 20)
        self.rolling_step = rolling_config.get("step", 10)

        # Transaction costs
        self.transaction_cost_bps = config_dict.get("transaction_cost_bps", 5.0)

        # Data source
        data_source = config_dict.get("data_source", {})
        self.use_long_history = data_source.get("use_long_history", True)

        # Output
        output_config = config_dict.get("output", {})
        self.output_directory = output_config.get("directory", "backtesting/results")
        self.save_trades = output_config.get("save_trades", False)

    def to_cli_args(self) -> Dict[str, Any]:
        """
        Convert config to dictionary matching run_backtests.py CLI arguments.

        Returns:
            Dictionary with keys matching argparse argument names
        """
        # Build period string
        period_parts = []
        for lookback in self.lookback_days:
            period_parts.append(str(lookback))
        if self.full_sample:
            period_parts.append("full")

        return {
            "tickers": ",".join(self.tickers),
            "strategies": ",".join(self.strategies),
            "portfolio_strategies": ",".join(self.portfolio_strategies),
            "periods": ",".join(period_parts),
            "market_periods": ",".join(self.market_regimes),
            "rolling_window": self.rolling_window if self.rolling_enabled else 0,
            "rolling_step": self.rolling_step,
            "transaction_cost_bps": self.transaction_cost_bps,
            "output_dir": self.output_directory,
            "use_long_history": self.use_long_history,
        }

    def __repr__(self) -> str:
        return f"BacktestConfig(name='{self.name}', tickers={len(self.tickers)}, strategies={len(self.strategies)})"


def load_config(config_path: str) -> BacktestConfig:
    """
    Load and parse a YAML backtest configuration file.

    Args:
        config_path: Path to YAML config file

    Returns:
        BacktestConfig object

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        ValueError: If config is missing required fields
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path) as f:
        config_dict = yaml.safe_load(f)

    if not config_dict:
        raise ValueError(f"Empty or invalid config file: {config_path}")

    # Validate required fields
    if not config_dict.get("tickers"):
        raise ValueError("Config must specify 'tickers'")

    config = BacktestConfig(config_dict)

    # Validate that at least one strategy type is specified
    if not config.strategies and not config.portfolio_strategies:
        raise ValueError("Config must specify at least one strategy or portfolio_strategy")

    return config


def list_available_configs(config_dir: str = "backtesting/configs") -> list:
    """
    List all available YAML config files.

    Args:
        config_dir: Directory containing config files

    Returns:
        List of config file paths
    """
    config_path = Path(config_dir)
    if not config_path.exists():
        return []

    return sorted([str(p) for p in config_path.glob("*.yaml")])

#!/usr/bin/env python3
"""
Generate Intermarket Indicators

Calculates all intermarket indicators and saves them to JSON files
for backend analysis and frontend display.

Outputs:
- data/indicators.json - Backend reference
- frontend/public/data/indicators.json - Frontend display
"""

import json
from pathlib import Path
from indicators.intermarket import calculate_all_indicators


def main():
    """Generate and save indicator data."""
    print("Calculating intermarket indicators...")

    # Calculate all indicators
    indicators = calculate_all_indicators()

    # Save to backend data directory
    backend_path = Path('data/indicators.json')
    backend_path.parent.mkdir(parents=True, exist_ok=True)
    with open(backend_path, 'w') as f:
        json.dump(indicators, indent=2, fp=f, default=str)
    print(f"✓ Saved to {backend_path}")

    # Save to frontend data directory
    frontend_path = Path('frontend/public/data/indicators.json')
    frontend_path.parent.mkdir(parents=True, exist_ok=True)
    with open(frontend_path, 'w') as f:
        json.dump(indicators, indent=2, fp=f, default=str)
    print(f"✓ Saved to {frontend_path}")

    # Print summary
    regime = indicators['market_regime']
    print("\n" + "=" * 80)
    print(f"MARKET REGIME: {regime['regime']}")
    print(f"Confidence: {regime['confidence'].upper()}")
    print(f"Interpretation: {regime['interpretation']}")
    print("=" * 80)

    print("\nIndividual Indicators:")
    for name, indicator in indicators['indicators'].items():
        print(f"  • {indicator['name']}: {indicator['signal'].replace('_', ' ').title()}")

    print("\n✓ Indicator generation complete!")


if __name__ == '__main__':
    main()

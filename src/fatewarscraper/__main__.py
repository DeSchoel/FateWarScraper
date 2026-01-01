import argparse
from .cli import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fate War Alliance Member Scraper")
    parser.add_argument("--gold", action="store_true", help="Include Gold Donation category in scan")
    parser.add_argument("--window", type=str, default="Fate War", help="Game window title")
    args = parser.parse_args()
    
    run(window_title=args.window, include_gold=args.gold)

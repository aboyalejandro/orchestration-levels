import os
import json
import argparse


def save_local(data, file_path):
    """Save JSON data to local file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Saved data to {file_path}")


def get_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local",
        action="store_true",
        help="Save files locally to /piwik-data instead of S3",
    )
    return parser.parse_args()

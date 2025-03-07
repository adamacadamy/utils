#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import subprocess
import sys

def create_flask_scaffold(parent: Path, structure: dict):
    """Create directory structure and files from the given structure dictionary."""
    stack = [(parent, structure)]
    while stack:
        current_parent, current_structure = stack.pop()
        for name, content in current_structure.items():
            path = current_parent / name
            if isinstance(content, dict):
                path.mkdir(parents=True, exist_ok=True)
                stack.append((path, content))
            else:
                path.touch(exist_ok=True)
                if content:
                    try:
                        # If content is a string, write it directly
                        path.write_text(content)
                    except TypeError:
                        # If content is a dict/list (from JSON), convert to formatted string
                        path.write_text(json.dumps(content, indent=4))

def setup_virtualenv(parent: Path, venv_name: str = "venv"):
    """Set up a virtual environment and install requirements."""
    venv_path = parent / venv_name
    try:
        subprocess.run(["python3", "-m", "venv", str(venv_path)], check=True)
        req_file = parent / "requirements.txt"
        if req_file.exists() and req_file.read_text().strip():
            subprocess.run([str(venv_path / "bin" / "pip"), "install", "-r", str(req_file)], check=True)
        print(f"Virtual environment created at {venv_path}")
        return venv_path
    except subprocess.CalledProcessError as e:
        print(f"Error setting up virtual environment: {e}")
        sys.exit(1)

def valid_json_file(file_path: str) -> Path:
    """Validate that the argument is a valid path to a JSON file."""
    path = Path(file_path)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"File '{file_path}' does not exist")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"'{file_path}' is not a file")
    if path.suffix.lower() != '.json':
        raise argparse.ArgumentTypeError(f"'{file_path}' is not a JSON file")
    return path

def valid_directory(dir_path: str) -> Path:
    """Validate that the argument is a valid existing directory path."""
    path = Path(dir_path)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Directory '{dir_path}' does not exist")
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"'{dir_path}' exists but is not a directory")
    return path

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Create a Flask project scaffold from a JSON structure file"
    )
    parser.add_argument(
        "json_file",
        type=valid_json_file,
        help="Path to the JSON file containing the project structure"
    )
    parser.add_argument(
        "--destination",
        "-d",
        type=valid_directory,
        default=Path.cwd(),
        help="Destination directory for the project (must exist, defaults to current directory)"
    )

    args = parser.parse_args()

    # Read and validate JSON file
    try:
        with args.json_file.open("r") as f:
            project_structure = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.json_file}': {e}")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied accessing '{args.json_file}'")
        sys.exit(1)

    # Create project structure
    destination = args.destination
    # Removed mkdir - validation is now handled by valid_directory
    
    print(f"Creating project structure in {destination}")
    create_flask_scaffold(destination, project_structure)
    print("Project structure created successfully")
    
    # Setup virtual environment
    venv_path = setup_virtualenv(destination)
    print("Project setup complete!")
    
    # Print usage instructions
    print("\nTo activate the virtual environment:")
    print(f"  source {venv_path / 'bin' / 'activate'}")
    print("To run the application:")
    print(f"  python {destination / 'run.py'}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import subprocess
import sys
import shutil

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
                        path.write_text(content)
                    except TypeError:
                        path.write_text(json.dumps(content, indent=4))

def setup_virtualenv(parent: Path, python_interpreter: str, venv_name: str = ".venv"):
    """Set up a virtual environment using the specified Python interpreter."""
    venv_path = parent / venv_name
    try:
        subprocess.run([python_interpreter, "-m", "venv", str(venv_path)], check=True)
        req_file = parent / "requirements.txt"
        if req_file.exists() and req_file.read_text().strip():
            subprocess.run([str(venv_path / "bin" / "pip"), "install", "-r", str(req_file)], check=True)
        print(f"Virtual environment created at {venv_path} using {python_interpreter}")
        return venv_path
    except subprocess.CalledProcessError as e:
        print(f"Error setting up virtual environment: {e}")
        sys.exit(1)

def find_gitignore_source() -> Path:
    """Find the first .gitignore file inside any 'python' directory within the current working directory."""
    current_dir = Path.cwd()
    for path in current_dir.rglob("python/.gitignore"):
        return path
    return None

def copy_gitignore(destination: Path):
    """Copy .gitignore from the first found 'python' directory."""
    gitignore_src = find_gitignore_source()
    if gitignore_src:
        gitignore_dest = destination / ".gitignore"
        shutil.copy(gitignore_src, gitignore_dest)
        print(f"Copied .gitignore from {gitignore_src} to {gitignore_dest}")
    else:
        print("Warning: No .gitignore found in any 'python' directory.")

def valid_json_file(file_path: str) -> Path:
    """Validate that the argument is a valid JSON file path."""
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
    parser = argparse.ArgumentParser(
        description="Create a Flask project scaffold from a JSON structure file"
    )
    parser.add_argument(
        "json_file",
        type=valid_json_file,
        nargs="?",  # Make it optional
        default=None,
        help="Path to the JSON file containing the project structure"
    )
    parser.add_argument(
        "--destination", "-d",
        type=valid_directory,
        default=Path.cwd(),
        help="Destination directory for the project (must exist, defaults to current directory)"
    )
    parser.add_argument(
        "--python", "-p",
        type=str,
        default="python3",
        help="Specify the Python interpreter for the virtual environment (default: python3)"
    )
    parser.add_argument(
        "--venv-only",
        action="store_true",
        help="Only create the virtual environment, skip project structure creation"
    )
    
    args = parser.parse_args()
    
    if args.venv_only:
        venv_path = setup_virtualenv(args.destination, args.python)
        print("Virtual environment setup complete!")
    else:
        if not args.json_file:
            print("Error: JSON file must be provided unless --venv-only is specified.")
            sys.exit(1)
        try:
            with args.json_file.open("r") as f:
                project_structure = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{args.json_file}': {e}")
            sys.exit(1)
        except PermissionError:
            print(f"Error: Permission denied accessing '{args.json_file}'")
            sys.exit(1)
        
        destination = args.destination
        
        print(f"Creating project structure in {destination}")
        create_flask_scaffold(destination, project_structure)
        print("Project structure created successfully")
        
        copy_gitignore(destination)
    
        venv_path = setup_virtualenv(args.destination, args.python)
        print("Project setup complete!")
    
    print("\nTo activate the virtual environment:")
    print(f"  source {venv_path / 'bin' / 'activate'}")
    print("To run the application:")
    print(f"  python {args.destination / 'run.py'}")

if __name__ == "__main__":
    main()

# python3 python/scaffolder.py --venv-only -d . --python python3
# python3 python/scaffolder.py python/template.json -d . --python python3

 
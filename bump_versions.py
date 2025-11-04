"""This is silly, but we version several different things here. This just runs through
and updates all the version numbers at once to the current date."""

import argparse
import datetime
import json
import subprocess


def parse_args() -> dict:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Bump all version numbers to today's date or specified version."
    )
    parser.add_argument(
        "--version",
        help="Specify a custom version instead of today's date.",
    )

    return vars(parser.parse_args())


def bump_npm(new_version: str) -> None:
    """Bump the version in package.json."""
    subprocess.run(
        ["npm", "version", new_version],
        cwd="wizard",
    )


def bump_python_version(new_version: str) -> None:
    """Bump the version in the Python package."""
    subprocess.run(["uv", "version", new_version])


def bump_mcp_json(new_version: str) -> None:
    """Bump the version in server.json."""
    server_json_path = "server.json"
    with open(server_json_path, "r") as f:
        content = json.load(f)

    content["version"] = new_version
    for obj in content["packages"]:
        if "version" in obj:
            obj["version"] = new_version

    with open(server_json_path, "w") as f:
        json.dump(content, f, indent=2)


def main() -> None:
    """Bump all version numbers to today's date."""
    args = parse_args()
    today = datetime.date.today().strftime("%Y.%-m.%-d")
    new_version = args["version"] if args["version"] else today
    print(f"Bumping all versions to {new_version}...")
    bump_npm(new_version)
    bump_python_version(new_version)
    bump_mcp_json(new_version)
    print(f"Bumped all versions to {new_version}")
    print("You need to commit and push.")


if __name__ == "__main__":
    main()

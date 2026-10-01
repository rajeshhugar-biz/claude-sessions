from pathlib import Path


def main():
    print("claude-practise: Claude API practice scripts\n")
    print("Run any script with:  uv run <path>\n")
    for path in sorted(Path(".").glob("Module*/*.py")):
        print(f"  {path.as_posix()}")


if __name__ == "__main__":
    main()

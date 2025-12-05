from core.constants.directories import Directories

def create_repo():
    if Directories.repo_dir.exists():
        print("Repository has already been initialized for this project!")
        return

    for dir in Directories.repo_dirs:
        dir.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    create_repo()

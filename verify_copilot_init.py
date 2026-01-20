from pathlib import Path
import shutil
from wai_cli.init import init_spoke

def verify():
    test_path = Path("verification_copilot_script").resolve()
    print(f"Testing init_spoke at: {test_path}")
    
    if test_path.exists():
        print("Cleaning up old test dir...")
        shutil.rmtree(test_path)
    test_path.mkdir()

    print("Running init_spoke...")
    try:
        init_spoke(test_path, is_framework=False, verbose=True)
        print("init_spoke completed.")
    except Exception as e:
        print(f"init_spoke failed: {e}")
        return

    # Check for copilot file
    copilot_file = test_path / '.github' / 'copilot-instructions.md'
    if copilot_file.exists():
        print(f"SUCCESS: {copilot_file} created.")
        print(f"Content preview: {copilot_file.read_text()[:50]}...")
    else:
        print(f"FAILURE: {copilot_file} NOT found.")

if __name__ == "__main__":
    verify()

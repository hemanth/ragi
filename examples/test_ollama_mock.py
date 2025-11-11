"""Test the ollama_example.py script logic without dependencies."""

import sys
import urllib.request


def check_ollama():
    """Check if Ollama is running."""
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=2)
        return True
    except Exception:
        return False


def main():
    """Test Ollama connectivity."""
    print("\n" + "=" * 60)
    print("Testing Ollama Connectivity")
    print("=" * 60 + "\n")

    # Check if Ollama is running
    print("Checking if Ollama is running...")
    if not check_ollama():
        print("❌ Ollama is not running!\n")
        print("This is expected if you haven't set up Ollama yet.")
        print("\nSetup instructions:")
        print("  1. Install: curl -fsSL https://ollama.com/install.sh | sh")
        print("  2. Pull model: ollama pull llama3.2")
        print("  3. Start Ollama (it usually auto-starts)")
        print("  4. Run the full example: python3 examples/ollama_example.py\n")
        return False

    print("✓ Ollama is running at http://localhost:11434")
    print("\nYou can run the full example:")
    print("  python3 examples/ollama_example.py\n")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

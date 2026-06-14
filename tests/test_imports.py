"""Test that all modules can be imported successfully."""
import sys
import os


def test_imports():
    """Test that all modules can be imported."""
    try:
        import scout
        print("✓ scout imported")
    except Exception as e:
        print(f"✗ scout import failed: {e}")
        raise

    try:
        import brief
        print("✓ brief imported")
    except Exception as e:
        print(f"✗ brief import failed: {e}")
        raise

    try:
        import listing_writer
        print("✓ listing_writer imported")
    except Exception as e:
        print(f"✗ listing_writer import failed: {e}")
        raise

    try:
        import mockup_factory
        print("✓ mockup_factory imported")
    except Exception as e:
        print(f"✗ mockup_factory import failed: {e}")
        raise

    try:
        import emailer
        print("✓ emailer imported")
    except Exception as e:
        print(f"✗ emailer import failed: {e}")
        raise

    try:
        import main
        print("✓ main imported")
    except Exception as e:
        print(f"✗ main import failed: {e}")
        raise

    print("All imports successful!")


if __name__ == '__main__':
    test_imports()

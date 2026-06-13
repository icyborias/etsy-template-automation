import os
from listing_writer import generate_listing


def test_generate_listing_writes_file(tmp_path):
    path = generate_listing("test_niche", "Sample Title")
    assert os.path.exists(path)
    import json

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "title" in data


if __name__ == '__main__':
    test_generate_listing_writes_file(None)

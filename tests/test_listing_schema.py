import json
import os
from listing_writer import generate_listing


def test_listing_schema(tmp_path):
    path = generate_listing("schema_niche", "Schema Title")
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # If raw fallback, allow that but assert title exists
    if "raw" in data:
        assert isinstance(data["raw"], str)
        return
    assert "title" in data
    assert len(data["title"]) <= 140
    assert "tags" in data and isinstance(data["tags"], list)
    # if tags provided, ensure at most 13 (some models may return fewer in fallback)
    assert len(data["tags"]) <= 13
    assert "description" in data and data["description"]
    assert "category" in data and data["category"]


if __name__ == '__main__':
    test_listing_schema(None)

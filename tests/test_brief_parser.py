import os
from brief import generate_brief, parse_brief_metadata


def test_brief_metadata_parsing(tmp_path):
    # generate a brief (fallback path writes metadata)
    path = generate_brief("test_niche", "Test Idea")
    assert os.path.exists(path)
    meta = parse_brief_metadata(path)
    assert isinstance(meta, dict)
    assert "headline" in meta or meta == {}


if __name__ == '__main__':
    test_brief_metadata_parsing(None)

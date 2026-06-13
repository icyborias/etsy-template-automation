import json
import os
from scout import run_scan


def test_scout_structure(tmp_path):
    scout = run_scan()
    assert "date" in scout
    assert "niches" in scout and isinstance(scout["niches"], list)
    for n in scout["niches"]:
        assert "niche" in n and "results" in n
        assert isinstance(n["results"], list)
        for r in n["results"]:
            assert "keyword" in r and "opportunity" in r


if __name__ == '__main__':
    test_scout_structure(None)

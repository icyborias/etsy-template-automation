import os
import tempfile
from PIL import Image
from mockup_factory import make_mockups


def test_make_mockups_creates_files(tmp_path):
    # create a small dummy image
    inp = tmp_path / "template.png"
    img = Image.new("RGBA", (400, 600), (255, 0, 0, 255))
    img.save(inp)
    out = make_mockups(str(inp), "Test Title", "test_niche")
    assert len(out) == 8
    for p in out:
        assert os.path.exists(p)
        # file non-empty
        assert os.path.getsize(p) > 0


if __name__ == '__main__':
    test_make_mockups_creates_files(tempfile.gettempdir())

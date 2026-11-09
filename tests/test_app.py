import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitPagesTests(unittest.TestCase):
    def test_all_pages_render_without_exceptions(self):
        project_root = Path(__file__).resolve().parents[1]
        pages = [project_root / "streamlit_app.py"]
        pages.extend(sorted((project_root / "app_pages").glob("*.py")))

        for page in pages:
            with self.subTest(page=page.name):
                app = AppTest.from_file(str(page), default_timeout=60).run()
                self.assertFalse(
                    app.exception,
                    msg=f"{page.name} raised: "
                    + "; ".join(exception.message for exception in app.exception),
                )


if __name__ == "__main__":
    unittest.main()

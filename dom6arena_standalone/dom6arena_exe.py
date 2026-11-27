"""PyInstaller entry script; see build_exe.py.

Kept separate from ``dom6arena/entry.py`` because PyInstaller runs this file
as ``__main__``, where the package's relative imports need the parent on
``sys.path``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dom6arena.entry import main  # noqa: E402

raise SystemExit(main())

"""Single entry point of the frozen ``Dom6Arena.exe``.

Without arguments the config window opens.  ``--build [config]`` runs the
arena build in the current console (the GUI starts it that way, because the
build asks about battle reports on stdin), and ``--cli ...`` exposes the
``python -m dom6arena`` command line unchanged.
"""

from __future__ import annotations

import sys

from . import config


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    config.ensure_runtime_assets()

    if argv and argv[0] == '--build':
        from . import arena_build
        arena_build.main(argv[1] if len(argv) > 1 else config.CONFIG_PATH)
        return 0
    if argv and argv[0] == '--cli':
        from . import cli
        return cli.main(argv[1:])
    from . import arena_gui
    arena_gui.main(argv)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

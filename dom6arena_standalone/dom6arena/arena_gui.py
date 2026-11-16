"""Tkinter front end for ``arena_config.json``.

``python -m dom6arena.arena_build arena_config.json`` stays the command line
entry point; this window edits the same file and then runs exactly that
command in a console of its own (the build asks about battle reports on
stdin, so it needs a real console).

Every field is labelled with the ``_<key>说明`` text of the config, so the
GUI and the JSON stay in sync.  ``save`` gets a folder picker that lists
``savedgames``; the chosen folder name is what the tool copies.

Usage:  python -m dom6arena.arena_gui [arena_config.json]
"""

from __future__ import annotations

import json
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

if __package__ in (None, ''):
    # Started as a plain script (``python dom6arena/arena_gui.py`` or an
    # IDE's Run button): the relative import below needs the package parent.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = 'dom6arena'

from . import config, gamedata

DESC = '说明'
# Same labels as the Dom6 Inspector's nation menu: "<era code> <name>"
# ("EA Arcoscephale", "LA Gath"), which is the inspector's shortname
# (``eracode + ' ' + name``).  Era 0 pseudo nations have no code.
ERA_CODES = {1: 'EA', 2: 'MA', 3: 'LA'}
# Nation ids are what the config stores, but typing an id is error prone, so
# these fields are a dropdown of nation names that keeps the id behind the
# label.
NATION_KEYS = {'own_nation', 'enemy_nation'}
# Shown for reference but not editable: the arena map is a fixed, hand made
# map folder and every config uses the same one.
READONLY_KEYS = {'map'}


def _kind(key: str, value) -> str:
    """Which widget a config value needs."""
    if isinstance(value, bool):
        return 'bool'
    if isinstance(value, int):
        return 'int'
    if isinstance(value, str):
        return 'str'
    if isinstance(value, list) and key != 'extra_units' and all(
            isinstance(v, int) and not isinstance(v, bool) for v in value):
        return 'ints'
    return 'json'


class ArenaGui:
    def __init__(self, root: tk.Tk, path: Path):
        self.root = root
        self.path = path
        self.raw = json.loads(path.read_text(encoding='utf-8'))
        self.fields: list[tuple[str | None, str, object]] = []
        self.status = tk.StringVar()

        root.title(f'Dominions 6 arena - {path.name}')
        root.geometry('920x820')

        head = ttk.Frame(root, padding=(12, 10, 12, 0))
        head.pack(fill='x')
        ttk.Label(head, text=f'配置文件: {path}',
                  font=('', 9, 'bold')).pack(anchor='w')
        if self.raw.get('_说明'):
            ttk.Label(head, foreground='#666', wraplength=860, justify='left',
                      text=str(self.raw['_说明'])).pack(anchor='w')

        body = ttk.Frame(root, padding=(12, 6, 12, 0))
        body.pack(fill='both', expand=True)
        canvas = tk.Canvas(body, highlightthickness=0)
        bar = ttk.Scrollbar(body, orient='vertical', command=canvas.yview)
        inner = ttk.Frame(canvas)
        window = canvas.create_window((0, 0), window=inner, anchor='nw')
        inner.bind('<Configure>',
                   lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',
                    lambda e: canvas.itemconfigure(window, width=e.width))
        canvas.configure(yscrollcommand=bar.set)
        canvas.pack(side='left', fill='both', expand=True)
        bar.pack(side='right', fill='y')
        canvas.bind_all('<MouseWheel>',
                        lambda e: canvas.yview_scroll(-e.delta // 120, 'units'))

        others = ttk.LabelFrame(inner, text='其它', padding=(10, 6))
        others_packed = False
        for key, value in self.raw.items():
            if key.startswith('_'):
                continue
            desc = (value.get(f'_{DESC}') if isinstance(value, dict) else '') \
                or self.raw.get(f'_{key}{DESC}', '')
            if isinstance(value, dict):
                frame = ttk.LabelFrame(inner, text=key, padding=(10, 6))
                frame.pack(fill='x', pady=4)
                if desc:
                    ttk.Label(frame, text=desc, wraplength=840,
                              justify='left', foreground='#666').pack(anchor='w')
                for sub_key, sub_value in value.items():
                    if sub_key.startswith('_'):
                        continue
                    self._field(frame, key, sub_key, sub_value,
                                value.get(f'_{sub_key}{DESC}', ''))
            else:
                if not others_packed:
                    others.pack(fill='x', pady=4)
                    others_packed = True
                self._field(others, None, key, value, desc)

        foot = ttk.Frame(root, padding=(12, 8, 12, 10))
        foot.pack(fill='x')
        ttk.Button(foot, text='启动', command=self.launch).pack(side='left')
        ttk.Button(foot, text='只保存配置',
                   command=self.save).pack(side='left', padx=6)
        ttk.Button(foot, text='退出', command=root.destroy).pack(side='right')
        ttk.Label(foot, textvariable=self.status,
                  foreground='#1a7f37').pack(side='left', padx=12)

    # -- widgets ---------------------------------------------------------
    def _field(self, parent: ttk.Frame, section: str | None, key: str,
               value, desc: str) -> None:
        box = ttk.Frame(parent)
        box.pack(fill='x', pady=3)
        ttk.Label(box, text=key, font=('', 9, 'bold')).pack(anchor='w')
        if desc:
            ttk.Label(box, text=desc, wraplength=840, justify='left',
                      foreground='#666').pack(anchor='w')
        row = ttk.Frame(box)
        row.pack(fill='x', pady=(2, 0))
        kind = _kind(key, value)

        if key in NATION_KEYS:
            self._nation_combo(row, section, key, int(value))
            return

        if kind == 'bool':
            var = tk.BooleanVar(value=bool(value))
            ttk.Checkbutton(row, variable=var).pack(side='left')
            self.fields.append((section, key, lambda v=var: v.get()))
            return

        if kind == 'json':
            text = tk.Text(row, height=3, wrap='none')
            text.insert('1.0', json.dumps(value, ensure_ascii=False))
            text.pack(fill='x')
            empty = [] if isinstance(value, list) else {}
            self.fields.append(
                (section, key,
                 lambda w=text, k=key, e=empty: _json_value(w, k, e)))
            return

        shown = ', '.join(str(v) for v in value) if kind == 'ints' else str(value)
        var = tk.StringVar(value=shown)
        entry = ttk.Entry(row, textvariable=var)
        if key in READONLY_KEYS:
            entry.configure(state='readonly')
        entry.pack(side='left', fill='x', expand=True)
        if key == 'save':
            ttk.Button(row, text='选择文件夹...',
                       command=lambda v=var: self._pick_save(v)).pack(
                side='left', padx=(6, 0))
        if kind == 'int':
            self.fields.append(
                (section, key, lambda v=var, k=key: _int_value(v, k)))
        elif kind == 'ints':
            self.fields.append(
                (section, key, lambda v=var, k=key: _ints_value(v, k)))
        else:
            self.fields.append((section, key, lambda v=var: v.get()))

    def _nation_combo(self, row: ttk.Frame, section: str | None, key: str,
                      current_id: int) -> None:
        """Dropdown of nation names; the config keeps the numeric id."""
        options: list[tuple[str, int]] = []
        for nation in sorted(gamedata.nations().values(),
                             key=lambda n: (n.era, n.name)):
            if nation.era == 0 and nation.id != current_id:
                continue          # Independents / Special Monsters
            options.append((_nation_label(nation), nation.id))
        labels = [label for label, _ in options]
        by_label = dict(options)
        current = next((label for label, nid in options if nid == current_id),
                       None)
        if current is None:       # mod nation unknown to gamedata
            current = f'#{current_id}'
            labels.insert(0, current)
            by_label[current] = current_id
        var = tk.StringVar(value=current)
        combo = ttk.Combobox(row, textvariable=var, values=labels,
                             state='readonly', height=24)
        combo.pack(side='left', fill='x', expand=True)
        self.fields.append(
            (section, key,
             lambda v=var, m=by_label: _combo_value(v, m)))

    def _pick_save(self, var: tk.StringVar) -> None:
        start = config.saved_games_dir()
        current = var.get().strip()
        initial = start / current if current and (start / current).is_dir() else start
        if not initial.is_dir():
            initial = config.PROJECT_ROOT
        chosen = filedialog.askdirectory(initialdir=str(initial),
                                         title='选择要拷贝的存档文件夹')
        if chosen:
            var.set(Path(chosen).name)

    # -- actions ---------------------------------------------------------
    def _collect(self) -> dict:
        cfg = json.loads(json.dumps(self.raw))     # keeps the 说明 entries
        for section, key, getter in self.fields:
            try:
                value = getter()
            except ValueError as exc:
                where = f'{section}.{key}' if section else key
                raise ValueError(f'{where}: {exc}') from None
            (cfg if section is None else cfg[section])[key] = value
        return cfg

    def save(self, quiet: bool = False) -> bool:
        try:
            cfg = self._collect()
        except ValueError as exc:
            messagebox.showerror('配置有误', str(exc), parent=self.root)
            return False
        self.path.write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8')
        self.status.set(f'已保存 {self.path.name}')
        if not quiet:
            messagebox.showinfo('已保存', str(self.path), parent=self.root)
        return True

    def launch(self) -> None:
        try:
            if not self.save(quiet=True):
                return
            cmd = [_console_python(), '-m', 'dom6arena.arena_build',
                   str(self.path)]
            kwargs = {'cwd': str(config.PROJECT_ROOT)}
            if sys.platform == 'win32':
                # cmd /k keeps the console (and any traceback) on screen after
                # the build ends, so a failure is never silent.
                cmd = ['cmd', '/k', *cmd]
                kwargs['creationflags'] = subprocess.CREATE_NEW_CONSOLE
            subprocess.Popen(cmd, **kwargs)
        except Exception as exc:                       # surfaced, never silent
            messagebox.showerror('无法启动', str(exc), parent=self.root)
            self.status.set('启动失败，见弹窗。')
            return
        self.status.set('已启动：战报选择等互动在新的控制台窗口里完成。')


def _console_python() -> str:
    """A python.exe even when the window itself was started by pythonw.exe.

    The build reads the battle report choices from stdin, so it needs a real
    console; pythonw.exe has none and would fail or run invisibly.
    """
    exe = Path(sys.executable)
    if exe.name.lower() == 'pythonw.exe':
        plain = exe.with_name('python.exe')
        if plain.is_file():
            return str(plain)
    return str(exe)


def _int_value(var: tk.StringVar, key: str) -> int:
    text = var.get().strip()
    try:
        return int(text)
    except ValueError:
        raise ValueError(f'需要整数，当前是 {text!r}') from None


def _ints_value(var: tk.StringVar, key: str) -> list[int]:
    text = var.get().strip().strip('[]')
    out: list[int] = []
    for part in text.replace(';', ',').split(','):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            raise ValueError(
                f'需要整数列表，例如 243, 244；当前是 {part!r}') from None
    return out


def _nation_label(nation) -> str:
    """The inspector's nation label: ``<era code> <name>`` (``LA Gath``)."""
    code = ERA_CODES.get(nation.era)
    return f'{code} {nation.name}' if code else nation.name


def _combo_value(var: tk.StringVar, mapping: dict[str, int]) -> int:
    text = var.get()
    if text not in mapping:
        raise ValueError('请从下拉列表里选择一个国家')
    return int(mapping[text])


def _json_value(widget: tk.Text, key: str, empty) -> object:
    text = widget.get('1.0', 'end').strip()
    if not text:
        return empty
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f'不是合法 JSON：{exc}') from None


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    path = Path(argv[0]) if argv else Path('arena_config.json')
    if not path.is_absolute():
        path = config.PROJECT_ROOT / path
    if not path.is_file():
        raise SystemExit(f'config not found: {path}')
    root = tk.Tk()
    ArenaGui(root, path)
    root.mainloop()


if __name__ == '__main__':
    main()

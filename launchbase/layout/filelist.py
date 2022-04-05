from typing import NamedTuple, List, Optional, Tuple
import pathlib
import prompt_toolkit.utils
from wcwidth import wcswidth


class FileItem(NamedTuple):
    path: pathlib.Path
    name_wc: int


class FileList:

    def __init__(self, width: int) -> None:
        self.dir: Optional[pathlib.Path] = None
        self.invalidated = prompt_toolkit.utils.Event(self)
        self.items: List[FileItem] = []
        self._text_cache = None
        self.width = width
        self.selected_index = 0

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, i: int) -> Optional[pathlib.Path]:
        if i < 0 or i >= len(self.items):
            return None
        return self.items[i][0]

    @property
    def selected(self) -> Optional[pathlib.Path]:
        if self.selected_index < 0 or self.selected_index >= len(self.items):
            return None
        return self.items[self.selected_index].path

    def get_text(self) -> List[Tuple[str, str]]:
        if not self.dir:
            return []

        if self.width == 0:
            return []

        if not isinstance(self._text_cache, list):

            def wc_padding(text, length):
                return text + ' ' * max(
                    0, (max(self.max_wc, self.width - 2) - length))

            def to_text(f: pathlib.Path, length: int) -> Tuple[str, str]:
                if f.is_symlink():
                    if f.is_dir():
                        return ('class:linkdir',
                                ' ' + wc_padding(f.name, length) + '\n')
                    else:
                        return ('class:linkfile',
                                ' ' + wc_padding(f.name, length) + '\n')
                else:
                    if f.is_dir():
                        return ('class:dir',
                                ' ' + wc_padding(f.name, length) + '\n')
                    else:
                        return ('class:file',
                                ' ' + wc_padding(f.name, length) + '\n')

            self._text_cache = []
            for f, l in self.items:
                fragment = to_text(f, l)
                new_len = len(fragment[1])
                # assert(new_len == self.width)
                self._text_cache.append(fragment)

        return self._text_cache

    def set_width(self, w):
        if w == self.width:
            return
        self.width = w
        self._text_cache = None

        def fire():
            self.invalidated.fire()

        asyncio.get_event_loop().call_soon_threadsafe(fire)

    def chdir(self, dir: pathlib.Path, select_target: Optional[pathlib.Path]):
        dir = dir.absolute()
        if dir.is_symlink():
            dir = dir.resolve()
        if self.dir == dir:
            return
        assert (dir.is_dir())
        items = []
        for i, f in enumerate(dir.iterdir()):
            items.append(FileItem(f, wcswidth(f.name)))
            if f == select_target:
                self.selected_index = i
        self.dir = dir
        self.items = items
        self.max_wc = max(l for f, l in self.items) if self.items else 0
        self._text_cache = None
        if select_target is None:
            self.selected_index = 0
        self.invalidated.fire()

    def go_parent(self, e):
        assert (self.dir)
        if self.dir.parent == self.dir:
            return
        self.chdir(self.dir.parent, self.dir)

    def go_selected(self, e):
        item = self.items[self.selected_index][0]
        if item and item.is_dir():
            try:
                self.chdir(item, None)
                self.selected_index = 0
            except PermissionError:
                # TODO
                pass

    def select(self, selected: int):
        if self.selected_index == selected:
            return
        if selected < 0 or selected >= len(self.items):
            return
        self.selected_index = selected
        self.invalidated.fire()

    def up(self, e):
        self.select(self.selected_index - 1)

    def down(self, e):
        self.select(self.selected_index + 1)

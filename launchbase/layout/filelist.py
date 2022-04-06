from typing import List, Optional, Tuple, Hashable
import pathlib
import prompt_toolkit.utils
import prompt_toolkit.formatted_text
from . import itemlist


class FileList(itemlist.ItemList):

    def __init__(self, width: int) -> None:
        self.dir: Optional[pathlib.Path] = None
        self.invalidated = prompt_toolkit.utils.Event(self)
        self.items: List[pathlib.Path] = []
        self.width = width
        self.selected_index = 0

    def get_list(self) -> Tuple[Hashable, prompt_toolkit.formatted_text.AnyFormattedText]:
        def to_text(f: pathlib.Path) -> Tuple[str, str]:
            if f.is_symlink():
                if f.is_dir():
                    return ('class:linkdir', ' ' + f.name)
                else:
                    return ('class:linkfile', ' ' + f.name)
            else:
                if f.is_dir():
                    return ('class:dir', ' ' + f.name)
                else:
                    return ('class:file', ' ' + f.name)
        return self.dir, [to_text(item) for item in self.items]

    @property
    def selected(self) -> Optional[pathlib.Path]:
        if self.selected_index < 0 or self.selected_index >= len(self.items):
            return None
        return self.items[self.selected_index]

    def chdir(self, dir: pathlib.Path, select_target: Optional[pathlib.Path]):
        dir = dir.absolute()
        if dir.is_symlink():
            dir = dir.resolve()
        if self.dir == dir:
            return
        assert (dir.is_dir())
        items = []
        for i, f in enumerate(dir.iterdir()):
            items.append(f)
            if f == select_target:
                self.selected_index = i
        self.dir = dir
        self.items = sorted(items, key=lambda item: item.name)
        if select_target is None:
            self.selected_index = 0
        self.invalidated.fire()

    def go_parent(self, e):
        assert (self.dir)
        if self.dir.parent == self.dir:
            return
        self.chdir(self.dir.parent, self.dir)

    def go_selected(self, e):
        item = self.items[self.selected_index]
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

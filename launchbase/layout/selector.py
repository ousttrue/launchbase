from typing import Iterable, List, Tuple, Optional, cast
import pathlib
import prompt_toolkit.layout
import prompt_toolkit.utils
from .filelist import FileList


class Selector(prompt_toolkit.layout.FormattedTextControl):

    def __init__(self, kb: prompt_toolkit.key_binding.KeyBindings,
                 items: FileList) -> None:
        super().__init__(items.get_text,
                         focusable=True,
                         get_cursor_position=lambda: prompt_toolkit.
                         data_structures.Point(0, self.items.selected_index))
        self.has_focus = prompt_toolkit.filters.has_focus(self)
        self.items = items
        self.kb = kb

        self._keybind(self.items.go_parent, 'left')
        self._keybind(self.items.go_parent, 'h')
        self._keybind(self.items.go_selected, 'l')
        self._keybind(self.items.go_selected, 'enter')
        self._keybind(self.items.up, 'up')
        self._keybind(self.items.up, 'k')
        self._keybind(self.items.down, 'down')
        self._keybind(self.items.down, 'j')

    def _keybind(self, callback, *args, **kw):
        self.kb.add(*args, **kw, filter=self.has_focus)(callback)

    def get_invalidate_events(
            self) -> Iterable[prompt_toolkit.utils.Event[object]]:
        return [self.items.invalidated]

    def create_content(self, *args):
        content = super().create_content(*args)
        get_line = content.get_line

        def highlight_selected(line_index: int) -> List[Tuple[str, str]]:
            try:
                line = cast(List[Tuple[str, str]], get_line(line_index))
                if line_index == self.items.selected_index:
                    line = [(style + ' class:selected', text)
                            for style, text in line]
                return line
            except IndexError:
                return []

        content.get_line = highlight_selected  # type: ignore
        return content

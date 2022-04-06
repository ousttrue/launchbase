from typing import Iterable, List, Tuple, Optional, cast
import pathlib
import prompt_toolkit.layout
import prompt_toolkit.utils
import prompt_toolkit.key_binding
import prompt_toolkit.data_structures
import prompt_toolkit.filters
from .itemlist import ItemList


class Selector(prompt_toolkit.layout.FormattedTextControl):

    def __init__(self, kb: prompt_toolkit.key_binding.KeyBindings,
                 items: ItemList) -> None:
        super().__init__(self.get_text,
                         focusable=True,
                         get_cursor_position=lambda: prompt_toolkit.
                         data_structures.Point(0, self.items.selected_index))
        self.has_focus = prompt_toolkit.filters.has_focus(self)
        self.items = items
        self.kb = kb

    def keybind(self, callback, *args, **kw):
        self.kb.add(*args, **kw, filter=self.has_focus)(callback)

    def get_text(self):
        key, items = self.items.get_list()
        return self.items.get_text()

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

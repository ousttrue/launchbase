from typing import Iterable, List, Tuple, Optional, cast, Hashable
import pathlib
from prompt_toolkit.application.current import get_app
from prompt_toolkit.data_structures import Point
import prompt_toolkit.layout
import prompt_toolkit.utils
import prompt_toolkit.key_binding
import prompt_toolkit.filters
import prompt_toolkit.cache
import prompt_toolkit.formatted_text
from .itemlist import ItemList


class Selector(prompt_toolkit.layout.FormattedTextControl):

    def __init__(self, kb: prompt_toolkit.key_binding.KeyBindings,
                 items: ItemList) -> None:
        super().__init__(lambda: '',
                         focusable=True,
                         get_cursor_position=lambda: Point(0, self.items.selected_index))
        self.has_focus = prompt_toolkit.filters.has_focus(self)
        self.items = items
        self.kb = kb

    def keybind(self, callback, *args, **kw):
        self.kb.add(*args, **kw, filter=self.has_focus)(callback)

    def get_invalidate_events(
            self) -> Iterable[prompt_toolkit.utils.Event[object]]:
        return [self.items.invalidated]

    def get_text(self):

        return self.cache_text.get(key, create_text)

    def get_formatted_text_cached(self, width: int) -> prompt_toolkit.formatted_text.StyleAndTextTuples:
        key, src = self.items.get_list()

        def focus(style: str, i: int):
            if i == self.items.selected_index:
                style += ' class:selected'
            return style

        def create_line(text: str, width: int):
            # return text + '\n'
            from wcwidth import wcswidth
            padding = max(0, width - wcswidth(text))
            return text + ' ' * padding + '\n'

        def create_text() -> prompt_toolkit.formatted_text.StyleAndTextTuples:
            return [(focus(style, i), create_line(text, width)) for i, (style, text) in enumerate(src)]

        return self._fragment_cache.get(get_app().render_counter, create_text)

    def create_content(self, width: int, height: Optional[int]) -> prompt_toolkit.layout.UIContent:
        # Get fragments
        fragments_with_mouse_handlers = self.get_formatted_text_cached(width)
        fragment_lines_with_mouse_handlers = list(
            prompt_toolkit.formatted_text.split_lines(
                fragments_with_mouse_handlers)
        )

        # Strip mouse handlers from fragments.
        fragment_lines: List[prompt_toolkit.formatted_text.StyleAndTextTuples] = [
            [(item[0], item[1]) for item in line]
            for line in fragment_lines_with_mouse_handlers
        ]

        # Keep track of the fragments with mouse handler, for later use in
        # `mouse_handler`.
        self._fragments = fragments_with_mouse_handlers

        # If there is a `[SetCursorPosition]` in the fragment list, set the
        # cursor position here.
        def get_cursor_position(
            fragment: str = "[SetCursorPosition]",
        ) -> Optional[Point]:
            for y, line in enumerate(fragment_lines):
                x = 0
                for style_str, text, *_ in line:
                    if fragment in style_str:
                        return Point(x=x, y=y)
                    x += len(text)
            return None

        # If there is a `[SetMenuPosition]`, set the menu over here.
        def get_menu_position() -> Optional[Point]:
            return get_cursor_position("[SetMenuPosition]")

        cursor_position = (self.get_cursor_position or get_cursor_position)()

        # Create content, or take it from the cache.
        key = (tuple(fragments_with_mouse_handlers), width, cursor_position)

        def get_content() -> prompt_toolkit.layout.UIContent:
            return prompt_toolkit.layout.UIContent(
                get_line=lambda i: fragment_lines[i],
                line_count=len(fragment_lines),
                show_cursor=self.show_cursor,
                cursor_position=cursor_position,
                menu_position=get_menu_position(),
            )

        return self._content_cache.get(key, get_content)

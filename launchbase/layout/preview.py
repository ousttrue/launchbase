from typing import Optional
import pathlib
import prompt_toolkit.lexers
import prompt_toolkit.widgets


class Preview:

    def __init__(self) -> None:
        self.current_path: Optional[pathlib.Path] = None
        lexer = prompt_toolkit.lexers.DynamicLexer(
            lambda: prompt_toolkit.lexers.PygmentsLexer.from_filename(
                self.current_path or ".txt", sync_from_start=False))
        self.text_area = prompt_toolkit.widgets.TextArea(
            lexer=lexer,
            read_only=True,
            scrollbar=True,
            line_numbers=True,
        )

    def __pt_container__(self):
        return self.text_area

    def set_path(self, path: Optional[pathlib.Path]):
        if self.current_path == path:
            return
        self.current_path = path
        if not path:
            self.s = None
            self.text_area.text = ''
            return

        if path.is_dir():
            try:
                self.text_area.text = '\n'.join(f.name for f in path.iterdir())
            except Exception as e:
                self.text_area.text = str(e)
        else:
            try:
                self.text_area.text = path.read_text(encoding='utf-8')
            except Exception as e:
                self.text_area.text = str(e)

import asyncio
import pathlib
import prompt_toolkit
import prompt_toolkit.layout
import prompt_toolkit.key_binding
import prompt_toolkit.key_binding.vi_state
import prompt_toolkit.key_binding.bindings.scroll
import prompt_toolkit.styles
import prompt_toolkit.enums
import prompt_toolkit.cursor_shapes
import prompt_toolkit.buffer
import prompt_toolkit.filters
import prompt_toolkit.data_structures
import prompt_toolkit.utils
import prompt_toolkit.widgets
import prompt_toolkit.lexers

FL_WIDTH = 25


async def launch():
    kb = prompt_toolkit.key_binding.KeyBindings()

    from .layout.filelist import FileList
    fl = FileList(FL_WIDTH)

    @kb.add('Q')
    def quit(e: prompt_toolkit.key_binding.KeyPressEvent):
        e.app.exit()

    from .layout.selector import Selector
    selector = Selector(kb, fl)
    selector.keybind(fl.go_parent, 'left')
    selector.keybind(fl.go_parent, 'h')
    selector.keybind(fl.go_selected, 'l')
    selector.keybind(fl.go_selected, 'enter')
    selector.keybind(fl.up, 'up')
    selector.keybind(fl.up, 'k')
    selector.keybind(fl.down, 'down')
    selector.keybind(fl.down, 'j')

    from .layout.preview import Preview
    preview = Preview()

    kb.add('space')(prompt_toolkit.key_binding.bindings.scroll.scroll_forward)
    kb.add('b')(prompt_toolkit.key_binding.bindings.scroll.scroll_backward)

    @kb.add('tab', filter=prompt_toolkit.filters.has_focus(selector))
    def focus_preview(e: prompt_toolkit.key_binding.KeyPressEvent):
        e.app.layout.focus(preview)

    @kb.add('tab', filter=prompt_toolkit.filters.has_focus(preview))
    def focus_selector(e: prompt_toolkit.key_binding.KeyPressEvent):
        e.app.layout.focus(selector)

    def on_invalidated(_):
        preview.set_path(fl.selected)

    fl.invalidated += on_invalidated

    root = prompt_toolkit.layout.HSplit([
        prompt_toolkit.widgets.FormattedTextToolbar(lambda: f'{fl.dir}',
                                                    'class:addressbar'),
        prompt_toolkit.layout.VSplit([
            prompt_toolkit.layout.Window(selector,
                                         width=FL_WIDTH,
                                         always_hide_cursor=True),
            prompt_toolkit.layout.Window(char='|', width=1),
            preview,
        ])
    ])

    from .style import STYLE

    app = prompt_toolkit.Application(
        full_screen=True,
        layout=prompt_toolkit.layout.Layout(root, selector),
        key_bindings=kb,
        enable_page_navigation_bindings=True,
        style=STYLE,
        editing_mode=prompt_toolkit.enums.EditingMode.VI,
        cursor=prompt_toolkit.cursor_shapes.CursorShape.BLOCK,
    )

    def pre_run():
        app.vi_state.input_mode = prompt_toolkit.key_binding.vi_state.InputMode.NAVIGATION
        fl.chdir(pathlib.Path('.'), None)

    await app.run_async(pre_run=pre_run)


def main():
    asyncio.run(launch())


if __name__ == "__main__":
    main()

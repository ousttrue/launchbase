from typing import TYPE_CHECKING, Protocol, Tuple, Hashable, List
import abc
import prompt_toolkit.formatted_text

if TYPE_CHECKING:
    class Item(Protocol):
        pass


class ItemList(abc.ABC):
    @abc.abstractmethod
    def get_list(self) -> Tuple[Hashable, prompt_toolkit.formatted_text.StyleAndTextTuples]:
        raise NotImplementedError()

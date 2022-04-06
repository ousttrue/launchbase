from typing import TYPE_CHECKING, Protocol, Tuple, Hashable, List
import abc

if TYPE_CHECKING:
    class Item(Protocol):
        pass


class ItemList(abc.ABC):
    @abc.abstractmethod
    def get_list(self) -> Tuple[Hashable, List['Item']]:
        raise NotImplementedError()

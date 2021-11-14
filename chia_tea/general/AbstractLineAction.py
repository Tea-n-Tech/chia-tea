from abc import ABC, abstractmethod

from ..models.ChiaWatchdog import ChiaWatchdog


class AbstractLineAction(ABC):
    """Action to be applied on log lines"""

    @abstractmethod
    def is_match(self, line: str) -> bool:
        """Checks if a line is matching the Action

        Parameter
        ---------
        line : str
            line to be checked for a match

        Returns
        -------
        is_match : bool
            if the line is a match
        """
        raise NotImplementedError()

    @abstractmethod
    def apply(
        self: "AbstractLineAction",
        line: str,
        chia_dog: ChiaWatchdog,
    ):
        """Apply the line action

        Parameter
        ---------
        line : str
            line from which information will be extracted
        chia_dog : ChiaWatchdog
            chia watchdog to be modified
        """
        raise NotImplementedError()

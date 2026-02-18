from core import Tx
from abc import ABC, abstractmethod

class Heuristic(ABC):
    complexity = "none"
    accuracy = 0

    @abstractmethod
    def apply(self, tx: Tx):
        """
        Applies and returns the result of the heuristic.
        
        :param self: Description
        :param tx: Transaction which will be applied the heuristic.
        :type tx: Tx
        """
        pass


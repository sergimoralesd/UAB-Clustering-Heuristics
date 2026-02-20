from uab_heuristics.core import Tx
from abc import ABC, abstractmethod

class Heuristic(ABC):
    __complexity__ = "none"
    __accuracy__ = 0

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def complexity(self):
        return self.__complexity__
    
    @property
    def accuracy(self):
        return self.__accuracy__


    @abstractmethod
    def apply(self, tx: Tx):
        """
        Applies and returns the result of the heuristic.
        
        :param self: Description
        :param tx: Transaction which will be applied the heuristic.
        :type tx: Tx
        """
        pass


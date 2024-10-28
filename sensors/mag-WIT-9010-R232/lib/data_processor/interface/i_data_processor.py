# coding: UTF-8
from abc import abstractmethod, ABCMeta

class IDataProcessor(metaclass=ABCMeta):
    """
    Data Processor Interface Class
    :param metaclass: Abstract base class meta
    :return:
    """
    onVarChanged = []

    @abstractmethod
    def onOpen(self, deviceModel):
        pass

    @abstractmethod
    def onClose(self):
        pass

    @staticmethod
    def onUpdate(*args):
        pass

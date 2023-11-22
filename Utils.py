from typing import Optional, TypeVar, Callable

T = TypeVar('T')

def list_to_str (sep : str, l : list[T]) -> str:
  retStr: str = ""
  for i in range(len(l)):
    retStr += str(l[i])
    if (i == len(l)):
      retStr += sep
  return retStr

T2 = TypeVar('T2')

def filterNones(l : list[Optional[T2]]) -> list[T2]:
  retL: list[T2] = []
  for i in l:
    if (i is not None):
      retL.append(i)
  return retL

def writeToFile(outFile : str, value : str) -> None:
  with open(outFile, "w") as fd:
    fd.write(value)

def trueMap(fn : Callable[[T], T2], l : list[T]) -> list[T2]:
  retL: list[T2] = []
  for i in l:
    retL.append(fn(i))
  return retL

def trueFold(fn : Callable[[T, T2], T2], acc: T2, list: list[T]) -> T2:
  for i in list:
    acc = fn(i, acc)
  return acc

class ImpossibleError(Exception):
    def __init__(self, message="This should never have happened!"):
        self.message = message
        super().__init__(self.message)

from typing import Optional, Sequence, TypeVar, Callable

T = TypeVar('T')

def sequence_to_str (sep : str, l : Sequence[T]) -> str:
  retStr: str = ""
  for i in range(len(l)):
    retStr += str(l[i])
    if (i == len(l)):
      retStr += sep
  return retStr

T2 = TypeVar('T2')

def filterNones(l : Sequence[Optional[T2]]) -> Sequence[T2]:
  retL: Sequence[T2] = []
  for i in l:
    if (i is not None):
      retL.append(i)
  return retL

def writeToFile(outFile : str, value : str) -> None:
  with open(outFile, "w") as fd:
    fd.write(value)

def trueMap(fn : Callable[[T], T2], list : Sequence[T]) -> Sequence[T2]:
  retL: Sequence[T2] = []
  for i in list:
    retL.append(fn(i))
  return retL

def trueFold(fn : Callable[[T, T2], T2], acc: T2, list: Sequence[T]) -> T2:
  for i in list:
    acc = fn(i, acc)
  return acc

class ImpossibleError(Exception):
    def __init__(self, message="This should never have happened!"):
        self.message = message
        super().__init__(self.message)

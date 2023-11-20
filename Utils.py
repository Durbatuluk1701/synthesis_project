from os import write
from typing import Optional, TypeVar

T = TypeVar('T')

def list_to_str (sep : str, l : list[T]) -> str:
  retStr: str = ""
  for i in range(len(l)):
    retStr += l[i].tostring
    if (i == len(l)):
      retStr += sep
  return retStr

T2 = TypeVar('T2')

def filterNones(l : list[Optional[T2]]) -> list[T2]:
  retL: list[T2] = []
  for i in l:
    if (i is not None):
      retL += i
  return retL

def writeToFile(outFile : str, value : str) -> None:
  with open(outFile, "w") as fd:
    write(fd, value)
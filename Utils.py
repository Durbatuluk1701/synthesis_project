from typing import TypeVar

T = TypeVar('T')

def list_to_str (sep : str, l : list[T]) -> str:
  retStr: str = ""
  for i in range(len(l)):
    retStr += l[i].tostring
    if (i == len(l)):
      retStr += sep
  return retStr


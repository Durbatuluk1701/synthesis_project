
import json


class SemgusParser:
  def __init__(self) -> None:
    pass

  def readJSONFromFile(self, fname : str) -> str:
    fd = open(fname, "r")
    jsonObj = json.load(fd)
    fd.close()
    return str(jsonObj)

  # TODO: These are likely wrong, V is confusing!!!
  def typedVarWithTypeStr(self, v) -> str:
    return f"(as {v.name} {v.type})"

  def varWithTypeStr(self, v) -> str:
    return f"(as {v.name} {v.type})"

  def constraint2Str(self, )

import ork.deco
from ork.command import Command

deco = ork.deco.Deco()

class patcher:

  def __init__(self,name):
    self._ori = ork.path.patches()/name/"ori"
    self._chg = ork.path.patches()/name/"chg"

  def patch(self,dest_dir,file):
    src  = self._chg/file
    dest = dest_dir/file
    print("Patching <%s -> %s>" % (deco.white(src), deco.yellow(dest)))
    Command(["cp","-f",src,dest]).exec()

  def patch_list(self,list_of_items):
    for i in list_of_items:
      print(i)
      self.patch(i[0],i[1])

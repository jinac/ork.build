###############################################################################
# Orkid Build System
# Copyright 2010-2020, Michael T. Mayers
# email: michael@tweakoz.com
# The Orkid Build System is published under the GPL 2.0 license
# see http://www.gnu.org/licenses/gpl-2.0.html
###############################################################################

from obt import dep, path, command, env

###############################################################################

class parsertl14(dep.StdProvider):
  name = "parsertl14"
  def __init__(self):
    super().__init__(parsertl14.name)
    #################################################
    srcroot = self.source_root
    #################################################
    class Builder(dep.BaseBuilder):
      def __init__(self,name):
        super().__init__(name)
      def build(self,srcdir,blddir,wrkdir,incremental):
        return dep.require(self._deps)
      def install(self,blddir):
        return command.run([ "cp",
                             "-r",
                             srcroot/"include"/"parsertl",
                             path.includes()
                             ],do_log=True)==0
    #################################################
    self._builder = Builder(parsertl14.name)
  ########################################################################
  @property
  def _fetcher(self):
    return dep.GithubFetcher(name=parsertl14.name,
                             repospec="tweakoz/parsertl14",
                             revision="master",
                             recursive=False)

  #######################################################################
  def areRequiredSourceFilesPresent(self):
    return (self.source_root/"README.md").exists()

  def areRequiredBinaryFilesPresent(self):
    return (path.includes()/"parsertl"/"parse.hpp").exists()

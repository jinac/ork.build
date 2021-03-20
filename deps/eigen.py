###############################################################################
# Orkid Build System
# Copyright 2010-2020, Michael T. Mayers
# email: michael@tweakoz.com
# The Orkid Build System is published under the GPL 2.0 license
# see http://www.gnu.org/licenses/gpl-2.0.html
###############################################################################
from ork import dep, path
###############################################################################
class eigen(dep.StdProvider):
  def __init__(self):
    name = "eigen"
    super().__init__(name)
    self._fetcher = dep.GithubFetcher(name=name,
                                      repospec="eigenteam/eigen-git-mirror",
                                      revision="3.3.7",
                                      recursive=False)
    self._builder = dep.CMakeBuilder(name)
    self._builder.requires(["lapack"])
  def compileenv(self): ##########################################################
    return {
        "INCLUDE_PATH": path.includes()/"eigen3"
    }

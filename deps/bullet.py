###############################################################################
# Orkid Build System
# Copyright 2010-2020, Michael T. Mayers
# email: michael@tweakoz.com
# The Orkid Build System is published under the GPL 2.0 license
# see http://www.gnu.org/licenses/gpl-2.0.html
###############################################################################

from ork import dep

###############################################################################

class bullet(dep.StdProvider):

  def __init__(self,miscoptions):
    name = "bullet"
    parclass = super(bullet,self)
    parclass.__init__(name=name,miscoptions=miscoptions)
    self._fetcher = dep.GitFetcher(name)
    self._fetcher._git_url = "https://github.com/bulletphysics/bullet3"
    self._fetcher._revision = "2.88"
    self._builder = dep.CMakeBuilder(name)

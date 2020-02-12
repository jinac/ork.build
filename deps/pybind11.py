###############################################################################
# Orkid Build System
# Copyright 2010-2018, Michael T. Mayers
# email: michael@tweakoz.com
# The Orkid Build System is published under the GPL 2.0 license
# see http://www.gnu.org/licenses/gpl-2.0.html
###############################################################################

VERSION = "master"

import os, tarfile
from ork import dep, host, path, cmake, git, make, command, pathtools
from ork.deco import Deco
from ork.wget import wget
from ork.command import Command

deco = Deco()

###############################################################################

class pybind11(dep.Provider):

  def __init__(self,options=None): ############################################

    parclass = super(pybind11,self)
    parclass.__init__(options=options)
    #print(options)
    self.source_dest = path.builds()/"pybind11"
    self.build_dest = path.builds()/"pybind11"/".build"
    self.manifest = path.manifests()/"pybind11"
    self.OK = self.manifest.exists()

  def __str__(self): ##########################################################

    return "PyBind11 (github-%s)" % VERSION

  def wipe(self): #############################################################
    os.system("rm -rf %s"%self.source_dest)

  def build(self): ##########################################################

    #########################################
    # fetch source
    #########################################

    if not self.source_dest.exists():
        git.Clone("https://github.com/pybind/pybind11",self.source_dest,VERSION)

    #########################################
    # prep for build
    #########################################

    ok2build = True
    if self.incremental():
        os.chdir(self.build_dest)
    else:
        pathtools.mkdir(self.build_dest,clean=True)
        pathtools.chdir(self.build_dest)

        cmakeEnv = {
            "CMAKE_BUILD_TYPE": "RELEASE",
            "BUILD_SHARED_LIBS": "ON",
        }

        cmake_ctx = cmake.context(root="..",env=cmakeEnv)
        ok2build = cmake_ctx.exec()==0

    #########################################
    # build
    #########################################

    if ok2build:
        self.OK = (make.exec("install")==0)

    return self.OK

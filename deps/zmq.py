###############################################################################
# Orkid Build System
# Copyright 2010-2018, Michael T. Mayers
# email: michael@tweakoz.com
# The Orkid Build System is published under the GPL 2.0 license
# see http://www.gnu.org/licenses/gpl-2.0.html
###############################################################################

VERSION = "v4.3.4"

import os, tarfile
from ork import dep, host, path, cmake, git, make, pathtools
from ork.deco import Deco
from ork.wget import wget
from ork.command import Command

deco = Deco()

###############################################################################

class zmq(dep.Provider):

  def __init__(self): ############################################
    super().__init__("zmq")
    self.declareDep("cmake")
    #print(options)
    build_root = path.builds()/"libzmq"
    self.source_root = build_root
    self.build_dest = build_root/".build"
    self.manifest = path.manifests()/"zmq"
    #self.sdk_dir = path.Path("/opt/nvencsdk")
    self.OK = self.manifest.exists()

  def __str__(self): ##########################################################

    return "zeromq and bindings (github-%s)" % VERSION

  def wipe(self): #############################################################
    os.system("rm -rf %s"%self.source_root)

  def build(self): ##########################################################

    #########################################
    # fetch source
    #########################################

    if not self.source_root.exists():
        git.Clone("https://github.com/zeromq/libzmq",self.source_root,VERSION)

    #########################################
    # prep for build
    #########################################

    ok2build = True
    if self.should_incremental_build:
        os.chdir(self.build_dest)
    else:

        pathtools.mkdir(self.build_dest,clean=True)
        os.chdir(self.build_dest)

        cmakeEnv = {
            "CMAKE_BUILD_TYPE": "RELEASE",
        }

        if host.IsDarwin:
          cmakeEnv["WITH_TLS"]="OFF"

        cmake_ctx = cmake.context("..",env=cmakeEnv)
        ok2build = cmake_ctx.exec()==0

    #########################################
    # build
    #########################################

    if ok2build:
        self.OK = (make.exec("install")==0)
        
    return self.OK

  def linkenv(self): ##########################################################
    LIBS = ["zmq"]
    return {
        "LIBS": LIBS,
        "LFLAGS": ["-l%s"%item for item in LIBS]
    }

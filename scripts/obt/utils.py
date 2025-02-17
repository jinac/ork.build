###############################################################################
# Orkid Build System
# Copyright 2010-2018, Michael T. Mayers
# email: michael@tweakoz.com
# The Orkid Build System is published under the GPL 2.0 license
# see http://www.gnu.org/licenses/gpl-2.0.html
###############################################################################


import os, sys, string
import shutil, glob
import platform
import subprocess
import os
import errno
import time
import sys
import xml.etree.ElementTree as xml
import hashlib

import obt.common
from obt.command import Command

deco = obt.deco.Deco()

def is_irix():
	return sys.platform.find("irix")!=-1

def pexec(args):
    return subprocess.Popen(string.split(args), stdout=subprocess.PIPE, shell=True).communicate()[0]

num_cores = 1

if is_irix():
	num_cores_str = pexec( 'hinv -c processor' )
	f = string.split(num_cores_str)[0]
	num_cores = int(float(f))
	print("IRIX num_cores<%d>" % num_cores)
else:
   try:
     import multiprocessing
     num_cores = multiprocessing.cpu_count()
   except ImportError:
     print("No MultiProcessing module - building with 1 core")
  


from obt.build.manifest import *
from obt.pathtools import *

import select
import fcntl

stage_dir = os.environ["OBT_STAGE"]

###############################################################################

#MARK: yo

SYSTEM = platform.system()

def IsCygwin():
	return SYSTEM.lower().find( "cygwin" )!=-1

def IsWindows():
	iswin = SYSTEM.lower().find( "windows" )!=-1
	ismso = SYSTEM.lower().find( "microsoft" )!=-1
	return iswin or ismso

###########################################

def folder_tree(rootpath):
	ret = list()
	ret.append(rootpath)
	#print "folder_tree<%s>"%rootpath
	for root, subFolders, files in os.walk(rootpath):
		for folder in subFolders:
			f = os.path.join(root,folder)
			ret.append(f)
			#print(f)
	return ret

###########################################
# check for obt.build projects
###########################################

def check_for_project(path):
	rval = None
	prj_manifest = "%s/obt.build.manifest"%path
	prj_scripts = os.path.abspath("%s/scripts"%path)
	#print "checking for project at<%s>" % deco.path(path)
	if os.path.exists(prj_manifest):
		#print "/////////////////////////////////////////"
		#print "// Projects Found !! <%s>" % deco.path(path)
		#print "/////////////////////////////////////////"
		###############
		prj = manifests.add_project(path)
		manifest_tree = xml.parse(prj_manifest)
		###############
		#print manifest_tree
		rootElement = manifest_tree.getroot()
		prj.manifest_root = rootElement
		for a in rootElement.findall('depends_on'):
			#print dir(a)
			depends = a.attrib["project"]
			#print "project<%s> depends<%s>" % (path,depends)

			manifests.depends(path,depends)
		###############
		prj.autoexecs = list()
		if os.path.exists(prj_scripts):
			sys.path.append(prj_scripts)
			append_env("PATH",prj_scripts)
			prj.scripts_folder = prj_scripts
			###############
			for a in rootElement.findall('autoexec'):
				scr = a.attrib["script"]
				scrpath = "%s/setenv.py" % prj_scripts
				if os.path.exists(scrpath):
					prj.autoexecs.append(scrpath)
		###############
		#prj.libdir = os.path.abspath("%s/lib " % path)
		rval = prj
	return rval
###########################################
def check_for_projects(base):
	manifests.add_project("%s/obt.build"%base)
	paths = glob.glob("%s/*"%base)
	PRJ_LIBDIRS=" "
	setenv_scrs = list()
	for p in paths:
		if p!="scripts":
			if os.path.isdir(p):
				prj = check_for_project(p)
				if prj!=None:
					if hasattr(prj,"libdir"):
						PRJ_LIBDIRS += prj.libdir
					if hasattr(prj,"autoexecs"):
						for a in prj.autoexecs:
							#print "execute autoexec<%s>" % a
							setenv_scrs.append(a)
	#append_env("PRJ_LIBDIRS",PRJ_LIBDIRS)
	for i in setenv_scrs:
		#print "exec child setenv <%s>" % i
		execfile(i)
	#print "PRJ_LIBDIRS<%s>" % PRJ_LIBDIRS
############################
def untar(arc,strip=False):
	is_gz = arc.find(".gz")>0
	is_bz2 = arc.find(".bz2")>0
	cmd = ["tar","--extract","--verbose"]
	if is_gz:
		cmd += ["--ungzip"]
	elif is_bz2:
		cmd += ["--bzip2"]
	if strip:
		cmd += ["--strip-components=1"]
	cmd += ["-f",arc]
	Command(cmd).exec()
#############################################
class context:
	############################
	def __init__(self,dl_dir):
		self.dl_dir = dl_dir
		self.opt_apts = False
		self.opt_exts = False
		self.opt_force = False

		self.nargs = len(sys.argv)
		if 1 == self.nargs:
			print("usage: (all | apts | exts | assets) [force]")
		else:
			for i in range(1,self.nargs,1):
				arg = sys.argv[i]
				if arg=="all":
					self.opt_apts = True
					self.opt_exts = True
				elif arg=="apts":
					self.opt_apts = True
				elif arg=="exts":
					self.opt_exts = True
				elif arg=="force":
					self.opt_force = True
		#print "opt_force<%s>" % self.opt_force
	############################
	def md5_of_file(self, fname):
		fil = open(fname,"rb")
		data = fil.read()
		fil.close()
		md5obj = hashlib.md5()
		md5obj.update(data)
		return md5obj.hexdigest()
	############################
	def wget(self,url,outputname,desmd5):
		out_path = "%s/%s" % (self.dl_dir,outputname)
		actmd5 = False
		if os.path.exists(out_path):
			actmd5 = self.md5_of_file(out_path)
		if actmd5!=desmd5:  
			cmd = "wget %s -O %s" % (url,out_path)
			os.system(cmd)
			actmd5 = self.md5_of_file(out_path)
		print("<%s> DesiredMD5<%s>" % (outputname,desmd5))
		print("<%s> ActualMD5<%s>" % (outputname,actmd5))
	############################
	def gitget( self, url, dir, rev=None ):
		os.chdir(self.dl_dir)
		if self.opt_force:
			assert(False)
			os.system( "rm -rf %s" % dir )
		exists = os.path.exists(dir)
		if exists:
			os.chdir(dir)
			os.system("git pull origin master")
		else:
			os.system("git clone %s %s" % (url,dir))
			os.chdir(dir)
		if rev!=None:
			os.system( "git checkout %s" % rev )
	############################
	def svnget( self, url, dir, rev="HEAD" ):
		os.chdir(self.dl_dir)
		if self.opt_force:
			os.system( "rm -rf %s" % dir )
		exists = os.path.exists(dir)
		if False==exists:
			os.system("svn checkout %s %s" % (url,dir))
		os.chdir(dir)
		os.system("svn up -r %s" % rev )
	############################
	def hgget( self, url, dir, rev="" ):
		os.chdir(self.dl_dir)
		if self.opt_force:
			os.system( "rm -rf %s" % dir )
		exists = os.path.exists(dir)
		if False==exists:
			os.system( "hg clone %s %s" % (url,dir) )
		os.chdir(dir) 	
		os.system("hg update %s" % rev)
	############################

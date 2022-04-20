import ork.env
import ork.host
import ork.path
import ork.dep
import ork.deco
import os 

deco = ork.deco.Deco()

##########################################

class EnvSetup:
  def __init__(self,stagedir=None,
                    rootdir=None,
                    bindir=None,
                    scriptsdir=None,
                    disable_syspypath=False,
                    is_quiet=False,
                    project_name="NONE"):
    self.OBT_STAGE = stagedir 
    self.ROOT_DIR = rootdir 
    self.BIN_DIR = bindir 
    self.SCRIPTS_DIR = scriptsdir 
    self.DISABLE_SYSPYPATH=disable_syspypath
    self.IS_QUIET = is_quiet
    self.PROJECT_NAME = project_name
  ##########################################
  def install(self):
    ork.env.set("color_prompt","yes")
    ork.env.set("OBT_STAGE",self.OBT_STAGE)
    ork.env.set("OBT_BUILDS",self.OBT_STAGE/"builds")
    ork.env.set("OBT_ROOT",self.ROOT_DIR)
    ork.env.prepend("PATH",self.BIN_DIR )
    ork.env.prepend("PATH",self.OBT_STAGE/"bin")
    ork.env.prepend("LD_LIBRARY_PATH",self.OBT_STAGE/"lib")
    ork.env.prepend("LD_LIBRARY_PATH",self.OBT_STAGE/"lib64")
    ork.env.append("OBT_DEP_PATH",ork.path.root()/"deps")
    self.importProject(self.ROOT_DIR/".."/"obt.project")
    if ork.host.IsLinux:

      if ork.host.IsDebian:
        pkgcfgdir = ork.path.Path("/lib/x86_64-linux-gnu/pkgconfig")
      elif ork.host.IsGentoo:
        pkgcfgdir = ork.path.Path("/usr/lib64/pkgconfig")
      elif ork.host.IsAARCH64:
        pkgcfgdir = ork.path.Path("/usr/lib/pkgconfig")

      if pkgcfgdir.exists():
        ork.env.append("PKG_CONFIG_PATH",pkgcfgdir)
      pkgcfgdir = ork.path.Path("/usr/share/pkgconfig")
      if pkgcfgdir.exists():
        ork.env.append("PKG_CONFIG_PATH",pkgcfgdir)
    elif ork.host.IsDarwin:
      pkgcfgdir = ork.path.Path("/usr/local/lib/pkgconfig")
      if pkgcfgdir.exists():
        ork.env.append("PKG_CONFIG_PATH",pkgcfgdir)


    if ork.path.vivado_base().exists():
        ork.env.append("PATH",ork.path.vivado_base()/"bin")
    
    #####################################
    # Python Env Init
    #####################################
    
    if not ork.host.IsAARCH64:
      PYTHON = ork.dep.instance("python")
      #print(PYTHON)
      #if self.DISABLE_SYSPYPATH:
      #   ork.env.set("PYTHONHOME",PYTHON.home_dir)
    
    #####################################
    # Late init
    #####################################
    ork.env.set("PYTHONNOUSERSITE","TRUE")
    ork.env.set("PYTHONPATH",self.SCRIPTS_DIR)
    ork.env.prepend("PKG_CONFIG",self.OBT_STAGE/"bin"/"pkg-config")
    #ork.env.prepend("PKG_CONFIG_PREFIX",self.OBT_STAGE)
    ork.env.prepend("PKG_CONFIG_PATH",self.OBT_STAGE/"lib"/"pkgconfig")
    ork.env.prepend("PKG_CONFIG_PATH",self.OBT_STAGE/"lib64"/"pkgconfig")
    ork.env.append("PYTHONPATH",self.OBT_STAGE/"lib"/"python")
  ###########################################

  def importProject(self,prjdir):
    init_script = prjdir/"scripts"/"init_env.py"
    print(init_script)
    if init_script.exists():
      import importlib
      modulename = importlib.machinery.SourceFileLoader('modulename',str(init_script)).load_module()
      print(modulename)
      modulename.setup()
      #modul.setup()
  ###########################################
  def log(self,x):
    if not self.IS_QUIET:
       print(x)
  ###########################################
  def lazyMakeDirs(self):
    self.log(deco.bright("Making required directories"))
    (ork.path.prefix()/"lib").mkdir(parents=True,exist_ok=True)
    (ork.path.prefix()/"bin").mkdir(parents=True,exist_ok=True)
    (ork.path.prefix()/"include").mkdir(parents=True,exist_ok=True)
    ork.path.downloads().mkdir(parents=True,exist_ok=True)
    ork.path.builds().mkdir(parents=True,exist_ok=True)
    ork.path.manifests().mkdir(parents=True,exist_ok=True)
    ork.path.gitcache().mkdir(parents=True,exist_ok=True)
    ork.path.apps().mkdir(parents=True,exist_ok=True)
    ork.path.buildlogs().mkdir(parents=True,exist_ok=True)
  ###########################################
  def genBashRc(self,out_path):
    self.log(deco.bright("Generating bashrc"))
    bdeco = ork.deco.Deco(bash=True)

    BASHRC = ""

    ################################################
    # generate prompt
    ################################################

    stackindic = ""
    stacked = False
    if "OBT_STACK" in os.environ:
      stackindic = os.environ["OBT_STACK"]
      stacked = True
    PROMPT = bdeco.promptL('[ %s %s ]'%(stackindic,self.PROJECT_NAME))
    PROMPT += bdeco.promptC("\\w")
    PROMPT += bdeco.promptR("[$(parse_git_branch) ]")
    PROMPT += bdeco.bright("> ")

    ################################################
    # The sanity of this is a little debatable.
    #  on the one hand, some of the user's shell customizations are respected
    #  on the other hand this can perturb the build environment in other unexpected ways..
    ################################################

    BASHRC += 'source $HOME/.bashrc;\n' # source users's bash setup

    ################################################

    BASHRC += 'parse_git_branch() { git branch 2> /dev/null | grep "*" | sed -e "s/*//";};\n'

    BASHRC += "\nexport PS1='%s';\n" % PROMPT
    BASHRC += "alias ls='ls -G';\n"
    BASHRC += "complete -r -v\n"

    #########################################
    # statically defined goto and push methods
    #########################################

    dirs = {
        "root": "${OBT_ROOT}",
        "deps": "${OBT_ROOT}/deps",
        "stage": "${OBT_STAGE}",
        "builds": "${OBT_STAGE}/builds",
        "litex": "${OBT_STAGE}/builds/litex_env", # todo convert obt.litex.env.py to litex dep
    }

    #########################################
    # dynamic goto and pushd methods
    #  generated from individual deps
    #########################################

    depitems = ork.dep.DepNode.FindWithMethod("env_goto")
    for depitemk in depitems:
      depitem = depitems[depitemk]
      gotos = depitem.env_goto()
      dirs.update(gotos)

    #########################################

    for k in dirs:
        v = dirs[k]
        BASHRC += "obt.goto.%s() { cd %s; };" % (k,v)
        BASHRC += "obt.push.%s() { pushd %s; };" % (k,v)

    f = open(str(out_path), 'w')
    f.write(BASHRC)
    f.close()

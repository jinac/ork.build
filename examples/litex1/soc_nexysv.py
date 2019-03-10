#!/usr/bin/env python3

import os, sys, argparse
import ork.path
import ork.litex
import ork.vivado
import ork.command

build_dir = ork.path.builds()/"nexvsoc"
this_dir = os.path.dirname(os.path.realpath(__file__))

os.chdir(this_dir)

os.environ["build_dir"] = str(build_dir)

parser = argparse.ArgumentParser(description='nexysv SOCer')

parser.add_argument('--buildgw', action="store_true", help='build gateware' )
parser.add_argument('--uploadgw', action="store_true", help='upload gateware' )
parser.add_argument('--connect', action="store_true", help='connect to soc' )
parser.add_argument('--tty', metavar="tty", help='connect to soc' )
parser.add_argument('--litexinit', action="store_true", help='init litex env (and enter)' )
parser.add_argument('--litexshell', action="store_true", help='enter litex env' )
parser.add_argument('--litexupdate', action="store_true", help='update litex env' )

args = vars(parser.parse_args())

if len(sys.argv)==1:
    print(parser.format_usage())
    sys.exit(1)

#####################################
triple = {
    "cpu": "lm32",
    "platform": "nexys_video",
    "target": "base"
}
#####################################
def obtlxcmd(cmd):
    ork.command.run(["obt_litex_env.py",
                     "--cpu",triple["cpu"],
                     "--platform",triple["platform"],
                     "--target",triple["target"],
                     cmd ])
#####################################
if args["litexinit"]:
    obtlxcmd("--init")
elif args ["litexshell"]:
    obtlxcmd("--shell")
elif args ["litexupdate"]:
    obtlxcmd("--update")
#####################################
elif args["buildgw"]:
#####################################
    ork.litex.run( triple=triple,
                   cmdlist=["./nexys_video.py","--output-dir",build_dir] )
#####################################
elif args["uploadgw"]:
#####################################
    ork.vivado.run(["-mode","batch",
                    "-source","bit2svf_nexysv.tcl",
                    "-nojournal",
                    "-nolog"])
    ork.litex.run(triple=triple,
                  cmdlist=["sudo",ork.path.litex_env_dir()/"build"/"conda"/"bin"/"openocd",
                   "-f","./nexysv.cfg",
                   "-c","init",
                   "-c","'svf %s/gateware/top.svf'"%str(build_dir),
                   "-c","shutdown"])
#####################################
elif args["connect"]:
#####################################
    assert(args["tty"]!=None)
    ork.litex.run( triple=triple,
                   cmd="litex_term %s"%args["tty"] )

#!/usr/bin/python

import os
import sys
from compile_utility import *

def path_in_paths(path, paths, delimiter = ":"):
    if type(paths) == str:
        paths = paths.split(delimiter)
    path = path_normalize(path)
    for temp_path in paths:
        if path == path_normalize(temp_path):
            return True

    return False
    

def compile_nginx(args):
    nginx = args.nginx
    
    #make clean
    run("make clean", nginx)

    #configure
    configure = "./configure"
    ld_opt = ""
    cc_opt = ""
    if args.modsecurity:
        modsecurity = args.modsecurity
        modsecurity = os.path.join(modsecurity, "nginx/modsecurity")
        modsecurity = path_normalize(modsecurity)
        configure += " --add-module="+modsecurity
    if args.prefix:
        prefix = args.prefix
        prefix = path_normalize(prefix)
        configure += " --prefix="+prefix
    
    if args.pcre:
        pcre_config = os.path.join(args.pcre, "pcre-config")
        pcre_config = path_normalize(pcre_config)
        import subprocess
        if not os.path.exists(pcre_config):
            sys.stderr.write(pcre_config + " not exists\n")
            return
        pcre_prefix = path_normalize(subprocess.check_output([pcre_config, "--prefix"]).strip())
        pcre_libs = subprocess.check_output([pcre_config, "--libs"]).strip()
        pcre_include = os.path.join(pcre_prefix, "include")
        pcre_link = os.path.join(pcre_prefix, "lib")
        #1. add lib directory
        # run("export LD_LIBRARY_PATH=LD_LIBRARY_PATH:"+pcre_link)
        #or 2. remove softlinker
        #TODO more gracefule 
        if not pcre_link.startswith("/usr"):
            run("rm libpcre.so.1", pcre_link)
            run("mv libpcre.so.1.2.8 libpcre.so.1", pcre_link)
        #end 2
        ld_opt += pcre_libs
        cc_opt += "-I"+pcre_include+" -Wl,-rpath="+pcre_link
        configure += " --with-pcre "

    if ld_opt:
        configure += " --with-ld-opt=\""+ld_opt+"\" "
    if cc_opt:
        configure += " --with-cc-opt=\""+cc_opt+"\" "
    run(configure, nginx)

    #make -j
    run("make -j", nginx)
    #make install
    run("make install", nginx)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="compile nginx")
    parser.add_argument("--nginx", dest="nginx",default=os.getcwd())
    parser.add_argument("--modsecurity", dest="modsecurity", help="the directory of modsecurity")
    parser.add_argument("--pcre", dest="pcre", help="the directory of pcre-config")
    parser.add_argument("--prefix", dest="prefix", help="nginx install directory")
    
    args = parser.parse_args()
    compile_nginx(args)
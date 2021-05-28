#!/usr/bin/env python3

import os
import subprocess
from operator import itemgetter
import sys
import getopt

cache_path = '/var/cache/xbps/'

# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size#1094933
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def usage():
    print(sys.argv[0],'must specify -n for number of packages to keep')
    print("a value of 3 is suggested (current version +2)")
    print("-d false to actually delete cache items")
    print("using -c /some/dir changes the default cache location of " + cache_path)
    sys.exit(-1)

def main(argv):
    global cache_path
    keep_n = 1000
    dryRun = True
    try:
        opts, args = getopt.getopt(argv,"n:d:c:",[])
    except getopt.GetoptError:
        print("opts exception")
        usage()

    for opt, arg in opts:
        if opt == "-n":
            keep_n = int(arg)
        elif opt == "-d":
            dryRun = arg.lower() == 'true'
        elif opt == "-c":
            cache_path = arg

    if keep_n == 1000:  #hmmm
        usage()

    if keep_n<2:
        print("refusing to prune that much")
        exit(0)

    if not cache_path.endswith("/"):
        cache_path += "/"

    # all files ending .xbps
    file_names = os.listdir(cache_path)
    file_names = [fn for fn in file_names if fn.endswith('.xbps')]
    file_names.sort()

    # all package names in cache
    pkg_names = os.listdir(cache_path)
    pkg_names = [fn for fn in pkg_names if fn.endswith('.xbps')]
    pkg_names = [fn[0:fn.rfind('-')] for fn in pkg_names]
    pkg_names = list(set(pkg_names))

    # get a list of held packages
    s = subprocess.Popen([f"xbps-query --cachedir={cache_path} -H"], shell=True, stdout=subprocess.PIPE).stdout
    held = s.read().splitlines()
    held = [fn.decode("utf-8") for fn in held]
    held = [fn[0:fn.rfind('-')] for fn in held]

    # and a list of dependencies for held packages
    heldDeps=list()
    for hd in held:
        s = subprocess.Popen([f"xbps-query --cachedir={cache_path} --fulldeptree -x {hd}"], shell=True, stdout=subprocess.PIPE).stdout
        h = s.read().splitlines()
        h = [fn.decode("utf-8") for fn in h]
        h = [fn[0:fn.rfind('-')] for fn in h]
        heldDeps.extend(h)

    totalBytes = 0

    for pkg in pkg_names:
        # pkg = package name
        # vers = filenames
        if not pkg in held:
            # skip all held packages
            if not pkg in heldDeps:
                # code golf anyone ? next two line might be able to be done
                # in one step...
                vers = [pn for pn in file_names if pn.startswith(pkg)]
                vers = [pn for pn in vers if pkg == pn[0:pn.rfind('-')]]

                # sort by file creation date
                vers = [[pn,os.stat(cache_path+pn).st_ctime] for pn in vers]
                vers.sort(key=itemgetter(1))
                if (len(vers) > keep_n):
                    # TODO verbose option
                    #print (pkg, len(vers))
                    #for vfn in vers:
                    #    print('',vfn[0])



                    if dryRun==True:
                        print ('deletion candidates')
                        for vfn in vers[:-keep_n]:
                            print('',vfn[0])
                            totalBytes += os.path.getsize(cache_path+vfn[0])
                            totalBytes += os.path.getsize(cache_path+vfn[0]+".sig")
                    else:
                        print ('deletion list')
                        for vfn in vers[:-keep_n]:
                            print('',vfn[0])
                            os.remove(cache_path+vfn[0])
                            totalBytes += os.path.getsize(cache_path+vfn[0])
                            totalBytes += os.path.getsize(cache_path+vfn[0]+".sig")
            else:
                pass
                # TODO verbose option
                #print('package ',pkg,' is dependency of a held package so skipping')
        else:
            pass
            # TODO verbose option
            #print('package ',pkg,' is held so skipping')
    if (dryRun):
        print()
        print("No files were deleted (dry run)")
        print("potentially",sizeof_fmt(totalBytes),"bytes could be deleted")
    else:
        #print("deleting sig orphans")
        file_names = os.listdir(cache_path)
        file_names = [fn for fn in file_names if fn.endswith('.sig')]
        file_names.sort()
        count=0
        for sig in file_names:
            fn = os.path.splitext(cache_path + sig)[0]
            if not os.path.isfile(fn):
                fn+='.sig'
                os.remove(fn)
                count+=1
        print(count,"sig files removed")
        print("total of",sizeof_fmt(totalBytes),"bytes removed")

if __name__ == "__main__":
    main(sys.argv[1:])



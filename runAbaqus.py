import os,sys,glob,fnmatch,shutil
import toolbox
# tested on windows only
# the abaqus command must be reachable from command line from anywhere
extToKeep = ['inp','odb','msg','rpy','cae','txt','sta','dat']
defaultdirs = ['..\\myModels\\tryPython','..\\myModels\\tryInp']

sys.path.append(os.path.dirname(os.getcwd()))

def runAbaqusCmd(dirs,cmd,keep=False,gui=False):
    keepFName = ' '
    for file in loopOn(dirs):
        if not os.path.isfile(file): print "module %s not found!"%(file)
        else:
            pyKeep = keepFName+'.py'
            if pyKeep in file:
                continue
            runType = 'cae'
            if (toolbox.getFileExt(file)=='inp'):
                runType = 'inp'
                keepFName = toolbox.getFileName(file)
                pyfile = file.replace('.inp','.py')
            else: pyfile = file
            if cmd == 'rerun': 
                cleanWorkspace(file)
                runAbaqus(file,runType,keep=keep,gui=gui)
            elif cmd == 'run': runAbaqus(file,runType,keep=keep,gui=gui)
            elif cmd == 'clean': cleanWorkspace(file)
            elif cmd == 'postPro': 
                if os.path.isfile(pyfile): runPostPro(pyfile)
            elif cmd == 'runPost': 
                runAbaqus(file,runType,keep=keep,gui=gui)
                if os.path.isfile(pyfile): runPostPro(pyfile)
            elif cmd == 'rerunPost': 
                cleanWorkspace(file)
                runAbaqus(file,runType,keep=keep,gui=gui)
                if os.path.isfile(pyfile): runPostPro(pyfile)
            else: raise Exception("How the hell did I get here?")

def runAbaqus(file,runType,keep=False,gui=False):
    baseName = os.path.dirname(os.path.abspath(__file__))
    workspace =  toolbox.getWorkspace(file,baseName)
    if runType == 'cae':runCae(file,baseName,workspace,keep=keep,gui=gui)
    elif runType == 'inp':runInp(file,baseName,workspace,keep=keep)

def runCae(file,baseName,workspace,keep=False,gui=False):
    resFile = os.path.join(workspace,'abaqus.rpy')
    if runNeeded(file,workspace,resFile):    
        os.chdir(workspace)
        print "running abaqus cae on %s"%(toolbox.getFileName(file))
        cmd = 'abaqus cae '
        if (gui):
            cmd += 'script=%s -- %s'%(file,str(baseName))
        else:
            cmd += 'noGUI=%s -- %s > %s 2>&1'%(file,str(baseName),'exeCalls.txt')
        import subprocess
        p = subprocess.call(cmd, shell=True)
        if p: print("!! something has gone wrong, check exeCalls.txt and/or rpy file")

        if not keep: cleanFiles(file,baseName=baseName)
        os.chdir(baseName)
        
def runInp(file,baseName,workspace,keep=False):
    resFile = os.path.join(workspace,'exeCalls.txt')# no abaqus.rpy file for this method!!
    if (toolbox.getFileExt(file)=='inp') and (runNeeded(file,workspace,resFile) ): 
        shutil.copy(file, workspace)
        jobName = toolbox.getFileName(file)
        os.chdir(workspace)
        print "running abaqus on %s"%(jobName)
        cmd = 'abaqus job=%s interactive > %s 2>&1'%(jobName,'exeCalls.txt')

        import subprocess
        if toolbox.isUnix():
            p = subprocess.call(cmd, close_fds=True)
        else:
            p = subprocess.call(cmd, shell=True)
        if p: print("!! something has gone wrong, check exeCalls.txt and /or msg file")
        
        if not keep: cleanFiles(file,baseName=baseName)
        os.chdir(baseName)

def runNeeded(file,workspace,resFile):
    run = False
    if not(os.path.isdir(workspace)):
        try:
            os.makedirs(workspace)
        except WindowsError:
            print("file(s) locked!\n")
        run = True
    elif  (os.path.getmtime(resFile) < os.path.getmtime(file)) or not(os.path.isfile(resFile)):
        run = True
    return run

def runPostPro(file,workspace=None):
    baseName = os.path.dirname(os.path.abspath(__file__))
    if workspace is None:workspace =  toolbox.getWorkspace(file, baseName)
    if not os.path.isdir(workspace): raise Exception("cannot run postPro on empty workspace!")
    else :
        odbName = None
        for name in os.listdir(workspace):
            if name.split('.')[-1] == 'odb':
                odbName = name
                break
        if odbName is None: raise Exception("no odb file in %s!"%(workspace))
        versionInfo = sys.version_info
        assert versionInfo[0]==2,"need to use python 2.x version"
        module= toolbox.fileToModule(file)
        if versionInfo[1]<7:
            _temp = __import__(module, globals(), locals(), ['postPro'], -1)
        else:# in python 2.7 and above, __import__ should be replaced by importlib.import_module
            import importlib
            _temp = importlib.import_module(module)
        os.chdir(workspace)
        _temp.postPro(odbName)
        os.chdir(baseName)
 
def cleanWorkspace(file,baseName=os.getcwd(), verb=False):
    toolbox.cleanDir(toolbox.getWorkspace(file, baseName, verb))

def cleanFiles(file,baseName=os.getcwd(), verb=False):
    workspace = toolbox.getWorkspace(file, baseName, verb)
    if os.path.isdir(workspace):
        if verb: print "workspace: %s found"%(workspace)
        for path, subdirs, names in os.walk(workspace):
            for name in names:
                if name.split('.')[-1] not in extToKeep:
                    try:
                        os.remove(os.path.join(path, name))
                        if verb: print 'removing "%s"' % os.path.join(path, name)
                    except:
                        print 'warning: "%s" is locked' % os.path.join(path, name)
                        pass    
    else: raise Exception('workspace %s not found'%(workspace) )

def loopOn(modules):
    """
    loop on the modules and 
       - convert modules to paths ( intelSig.tests => ..\oo_nda\intelSig\tests)
       - expand dos wildcards  (apps\qs\cont* => [apps.qs.cont2, apps.qs.cont2ILU0, ...])
    """
    modules.sort()
    for dir in modules:
        dir = dir.replace('/',os.sep).replace('\\',os.sep)

        if dir.find(os.sep)!=-1 or fnmatch.fnmatch(dir,'*.py') or fnmatch.fnmatch(dir,'*.inp'):
            # case #1: module type = file, "runAbaqus run apps\qs\cont2.py"
            filemod = os.path.abspath(dir)
        else:
            # case #2: module type = module, "runAbaqus run apps.qs.cont2"
            filemod = toolbox.moduleToFile(dir)
        
        if filemod=='':
            print "ERROR: \"%s\" not found in path\n" % (dir)
            sys.exit()
        elif filemod.find('*')!=-1: 
            # case #3: module type with DOS wildcard, "runAbaqus run apps\qs\cont*"
            files=glob.glob(filemod)
            files.sort()
            for file in files:
                for mod in loopOn([file, ]): # recursive call
                    yield mod
        elif os.path.isdir(filemod):
            # case #4: module type = dir, "runAbaqus run apps\qs\" or "runAbaqus run apps.qs"
            files = os.listdir(filemod)
            files.sort()
            for file in files:                    
                fullfile = os.path.join(filemod, file)   
                for mod in loopOn([fullfile, ]):
                    yield mod
        else:
            # it's a file!
            if fnmatch.fnmatch(filemod,'*.py') or fnmatch.fnmatch(filemod,'*.inp'):
                if not (fnmatch.fnmatch(os.path.basename(filemod), '__init__.py')):
                    yield filemod 
        
def usage(progname):
    name = os.path.basename(progname)
    tab  = ' '
    print '\nusage:'
    print '%s%s [-keep][-gui]%s [run|clean|rerun|postPro|runPost]\n\t%s file1 file2  ...' % (tab,name,tab,tab)
    print '\noptions:'
    print '%s-gui  : run in interface mode'% (tab)
    print "%s-keep : keep all files (otherwise only keeps 'inp','odb','msg','rpy','cae','txt','sta','dat' )"% (tab)
    print "%s !! use -keep if a restart might be needed"% (tab)
    print '\ncommands:'
    print '%srun        : run some files - py modules or inp files (if not yet run)'% (tab)
    print '%sclean      : clean some modules'% (tab)
    print '%srerun      : clean + run'% (tab)
    print '%spostPro    : run a postPro function in some py modules (cwd = workspace)'% (tab)
    print "%s !! postPro function takes only odbName as argument (can have default arguments)!"% (tab)
    print '%srunPost    : run + postPro'% (tab)
    print '%srerunPost    : clean + run + postPro'% (tab)
    print '\nfiles: '
    print '%s-by module name   : e.g. apps.qs.cont2 or intelSig.tests.xfem'% (tab)
    print '%s-by file/dir name : e.g. ..\\oo_nda\\intelSig\\tests\\xfem'% (tab)
    print '%s !! if file name use with .py or .inp extension!'% (tab)
    print '%s-using wildcards  : e.g. apps\\qs\\cont*'% (tab)
    print

def main(gui=False,keep=False):
    i=0
    while i < len(sys.argv)-1 :
        i+=1
        cmd = sys.argv[i]
        if cmd ==  '-keep':
            keep = True
        elif cmd ==  '-gui':
            gui = True
        elif cmd ==  '-help':
            usage(sys.argv[0])
            sys.exit()	
        elif cmd in ['run','rerun','clean','postPro','runPost','rerunPost']:
            if len(sys.argv[i+1:])!=0: file = sys.argv[i+1:]
            else: file = defaultdirs
            runAbaqusCmd(file,cmd,keep=keep,gui=gui)
            sys.exit()
        else: raise Exception("unappropriate use, see -help")

if __name__ == "__main__":
    main(keep = False,gui = False)
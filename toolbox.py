"""
generic python tools
"""
import os,sys
#-----------------------------------------------------
def isUnix():
    import platform
    uname = platform.uname()
    return not (uname[0] == 'Windows' or uname[2] == 'Windows')
#-----------------------------------------------------
def fileToModule(file, verb=False):
    if verb: print 'os.path.sep=',os.path.sep
    file=os.path.abspath(file)
    if verb: print 'file=',file
    for dirname in sys.path:
        dirname = os.path.abspath(dirname).lower()
        if verb: print 'module in', dirname, '?',
        common = os.path.commonprefix( (file.lower(), dirname) )
        if common == dirname:
            if verb: print 'YES'
            strip = file[len(dirname):]
            if strip[0]==os.path.sep:
                strip=strip[1:]
            strip = os.path.splitext(strip)[0]
            strip = strip.replace(os.path.sep,'.')
            if verb: print 'module=', strip
            return strip
            break            
        else:
            if verb: print 'NO'
    return ''
#-----------------------------------------------------
def moduleToFile(module):
    for p in sys.path:
        #print 'testing %s' % p
        dir = os.path.join(p, module.replace('.',os.sep))
        dirini = os.path.join(dir, '__init__.py')
        file = '%s.py' % dir
        #print '\tdir=%s\n\tfile=%s' %(dir, file)
        if os.path.isfile(dirini):
            return dir
        elif os.path.isfile(file):
            return file
    return ''
#-----------------------------------------------------
def getWorkspace(file, baseName=os.getcwd(), verb=False):
    module = fileToModule(file,verb)
    wPath = os.path.join(baseName,os.path.join('workspace',module.replace('.','_')))
    workspace = os.path.abspath(wPath)
    if verb: print "toolbox.getWorkspace returns ",workspace
    return workspace
#-----------------------------------------------------
def modulePath(local_function):
    ''' returns the module path without the use of __file__.  Requires a function defined 
    locally in the module.
    from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module
    '''
    import inspect
    return os.path.abspath(inspect.getsourcefile(local_function))
#-----------------------------------------------------
def getFileName(fileWithExt):
    import os
    return os.path.basename(fileWithExt).split('.')[0]
#-----------------------------------------------------
def getFileExt(fileWithExt):
    import os
    return os.path.basename(fileWithExt).split('.')[-1]
#-----------------------------------------------------
def cleanDir(dir):
    try:
        import shutil
        if os.path.isdir(dir):
            print "cleaning ",dir
            shutil.rmtree(dir)
    except: # WindowsError if files in use
        pass

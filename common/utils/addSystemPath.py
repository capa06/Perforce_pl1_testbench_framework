#-------------------------------------------------------------------------------
# Author:       taken from the web
#               http://code.activestate.com/recipes/52662-dynamically-change-the-python-system-path/
# Adds the specified path to the Python system path
# if it is not already there. Takes into account
# terminating slashes and case (on Windows).
#-------------------------------------------------------------------------------

def AddSysPath(new_path):
    import sys, os

    # standardise
    new_path = os.path.abspath(new_path)

    # MS-Windows does not respect case
    if sys.platform == 'win32':
    	new_path = new_path.lower()

    # disallow bad paths
    do = -1
    if os.path.exists(new_path):
        do = 1

        # check against all paths currently available
        for x in sys.path:
            x = os.path.abspath(x)
            if sys.platform == 'win32':
            	x = x.lower()
            if new_path in (x, x + os.sep):
            	do = 0

        # add path if we don't already have it
        if do:
        	sys.path.append(new_path)
        	pass

    return do
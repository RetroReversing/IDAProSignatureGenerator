import fnmatch
import os
import subprocess
from subprocess import Popen, PIPE

verbose = False

def log_action(message):
    if verbose:
        print message

def execute_command(bashCommand):
    p = Popen(bashCommand.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate(b"input data that is passed to subprocess' stdin")
    rc = p.returncode
    return output
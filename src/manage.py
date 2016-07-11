import sys
from importlib import import_module
from subprocess import call
from textwrap import fill


# This seems redundant.

# Any tuple return value in any of these modules is the shutdown signal which
# will cause the assistant to speak the output first value and stop running.

# By standard, there should be one argument to every function,
# even if it is useless.


# Standard function, just stored here, not actually an action.
def import_or_install(module, package, description, capability):
    """Import module. If it fails to import, prompt user to install
    package and try again. The description argument gives a brief
    human-readable description of the module, and capability gives a
    human-readable description of what it can do.

    """
    imported = False
    try:
        import_module(module)
        imported = True
    except ImportError:
        print(fill("Your system does not have {} installed. "
                   "Without this module, this process will not {}."
                   .format(description, capability)))
        answer = input("Do you want to install it?")
        if answer.startswith(('Y', 'y')):
            call([sys.executable, '-m', 'pip', 'install',
                  '--upgrade', package])
            import_module(module)
            imported = True
    return imported


# Management Actions
# noinspection PyUnusedLocal
def app_close(void=None):
    return "Shutting down. See you later!"

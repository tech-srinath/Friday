=====
Plugins
=====

Plugin format
--------------

Every plugin has to have a certain layout in order to function properly.
In future, the plugin system might be modified slightly to take advantage of object-oriented design to reduce
the complexity of individual plugin classes.

File layout
~~~~~~~~~~~

For now, each plugin must follow the default layout for a `yapsy` plugin::

.. https://media.readthedocs.org/pdf/yapsy/latest/yapsy.pdf

    For a Standard plugin:
        * myplugin.yapsy-plugin
            - A plugin info file identical to the one previously described.
        * myplugin
            - A directory containing an actual Python plugin (ie with a __init__.py file that makes it importable). The upper namespace of the plugin should present a class inheriting the IPlugin interface (the same remarks apply here as in the previous case).
    For a Single file plugin:
        * myplugin.yapsy-plugin
            - A plugin info file which is identified thanks to its extension, see the Plugin Info File Format to see what should be in this file. The extension is customisable at the PluginManager‘s instanciation, since one may usually prefer the extension to bear the application name.
        * myplugin.py
            - The source of the plugin. This file should at least define a class inheriting the IPlugin interface. This class will be instanciated at plugin loading

Class layout
~~~~~~~~~~~~

The class which inherits from the IPlugin interface, as specified above, should have the following abstract setup::

    from yapsy.IPlugin import IPlugin


    class Plugin(IPlugin):
        def can_perform(self, friday, request) -> bool:
            pass

        def perform(self, friday, request):
            pass


Method descriptions
~~~~~~~~~~~~~~~~~~~

There are two methods which every plugin must have:

can_perform
    Determines whether the input plugin should be executed based on the current input.

perform
    Executes the functionality of the plugin

These two methods both receive the same input:

self
    A reference to the plugin's instance

friday
    A reference to the instance of the assistant,
    allowing plugins to only be executed when the assistant is in a specific state

request
    `The response from the API.AI service` formatted as a Python dictionary.

    .. https://docs.api.ai/docs/query#section-message-objects

Using these inputs, each plugin has access to everything the assistant has access to,
and full-featured plugins can be built using this system.

For more references, look at some example plugins included with this project.


Plugin Framework
================
A simple plugin framework for python.

PluginManager
-------------
The PluginManager class loads all plugins of a given type in a given package and
provides methods for managing them.

Plugin
------
The base plugin for the program should subclass the Plugin class. This base
plugin class should be given to the PluginManager when it is initialized (as
base_class).

Enabling/Disabling Plugins
--------------------------
``enabled`` should be set either by the PluginManager in ``on_load_plugin`` or by
``on_load`` in the Plugin itself. If a plugin is to be enabled or disabled after
loading, call enable() or disable(). Do not call enable/disable on load.

Dependencies
------------
Dependencies are static and can be set in a Plugin's depends list. They will be
resolved on-enable (if enabled through ``PluginManager.enable_plugin``) and will
be automatically enabled if ``enable_plugin`` is called with auto_deps=True.

PluginDependencyError will be raised if a dependency cannot be resolved.


#!/usr/bin/env python2
# encoding: utf-8
"""
A simple plugin framework.

The PluginManager will load all plugins of a given type in a given package and
provides methods for manageing them.

Plugins are responsible for determining weather or not they are enabled on
load and setting enabled appropriatly.

Plugins should NOT enable themselves in __init__. 

"""

__version__ = "0.1"
__author__ = "Steven Allen"
__email__ = "steven@stebalien.com"

class PluginDependencyError(Exception):
    def __init__(self, message="", depends=None):
        super(PluginDependencyError, self).__init__(message)
        self.depends = depends

class PluginError(Exception):
    def __init__(self, message="", plugin=None):
        super(PluginError, self).__init__(message)
        self.plugin = plugin

class PluginManager(dict):

    def __init__(self, base_class, plugin_package, instance_arguments = {}):
        self.plugin_package = plugin_package
        self.base_class = base_class
        self.instance_arguments = instance_arguments
        self.reload_plugins()

    def reload_plugins(self):
        """ Reload all plugins. """
        import pkgutil
        from inspect import isclass
        self.clear()

        # Instantiate
        for loader, module_name, is_pkg in pkgutil.iter_modules(self.plugin_package.__path__):
            for name, plugin_class in loader.find_module(module_name).load_module(module_name).__dict__.iteritems():
                if isclass(plugin_class) and issubclass(plugin_class, self.base_class) and plugin_class is not self.base_class and name not in self:
                    self[name] = plugin_class(**self.instance_arguments)

        # Load
        for plugin in self.itervalues():
            self.on_load_plugin(plugin)
            plugin.on_load()

        # Enable
        for plugin in self.enabled_plugins.itervalues():
            plugin.on_enable_plugin(plugin)
            plugin.on_enable()
    
    @property
    def enabled_plugins(self):
        """A dictionary of enabled plugins."""
        return {k:v for k,v in self.iteritems() if v.enabled}

    @property
    def disabled_plugins(self):
        """A dictionary of disabled plugins."""
        return {k:v for k,v in self.iteritems() if not v.enabled}

    def check_deps(self, plugin):
        """Check a plugins dependencies.

        Returns: a set of met and unmet dependencies.
        """
        plugin = self[plugin] if type(plugin) is str else plugin

        unmet = set()
        met   = set()

        for p in plugin.depends:
            if not p in met:
                new_met, new_unmet = self.check_deps(self, p)
                unmet.union(new_unmet)
                met.union(new_met)

        return met, unmet

    def enable_plugin(self, plugin, auto_deps=True, check_deps=True):
        """ Enable a plugin

        Arguments:
            plugin - the plugin to enable (name or instance)
            auto_deps   - automatically enable dependencies.
            check_deps  - check for dependency existance before doing anything.

        Returns: True if a plugin was enabled

        Raises:
            PluginDependencyError - if a plugin has unmet dependencies
            PluginError - if the requested plugin does not exist

        """
        try:
            plugin = self[plugin] if type(plugin) is str else plugin
        except KeyError:
            raise PluginError("Plugin '%s' does not exist." % plugin, plugin)

        if plugin.enabled:
            return False

        if auto_deps:
            if check_deps:
                _, unmet = self.check_deps(plugin)
                if unmet:
                    raise PluginDependencyError("Required plugins not found: %s" % ", ".join(unmet), unmet)
            for p in plugin.depends:
                self.enable_plugin(p, auto_deps)
        else:
            unmet = set(self.disabled_plugins).intersect(set(plugin.depends))
            if unmet:
                raise PluginDependencyError("Unmet Dependencies: %s" % ", ".join(unmet), unmet)

        if plugin.enable():
            self.on_enable(plugin)
            return True
        return False

    def disable_plugin(self, plugin):
        """ Disable a plugin
        
        Arguments:
            plugin - the plugin to disable (name or instance)

        Returns: True if a plugin was disabled

        Raises:
            PluginError - if the requested plugin does not exist
        """
        try:
            plugin = self[plugin] if type(plugin) is str else plugin
        except KeyError:
            raise PluginError("Plugin '%s' does not exist." % plugin)
        if plugin.disable():
            self.on_disable(plugin)
            return True
        return False

    def on_enable_plugin(self, plugin):
        """Called when a plugin is enabled."""
        pass

    def on_disable_plugin(self, plugin):
        """Called when a plugin is disabled."""
        pass

    def on_load_plugin(self, plugin):
        """Called when a plugin is loaded."""
        pass

class Plugin(object):
    depends = ()
    enabled = False

    def enable(self):
        """Enable the plugin."""
        if not self.enabled:
            self.enabled = True
            self.on_enable()
            return True
        return False

    def disable(self):
        """Disable the plugin."""
        if self.enabled:
            self.enabled = False
            self.on_disable()
            return True
        return False

    def on_load(self):
        """Called when the plugin is loaded."""
        pass

    def on_enable(self):
        """Called when the plugin is enabled."""
        pass

    def on_disable(self):
        """Called when the plugin is disabled."""
        pass



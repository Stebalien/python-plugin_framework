#!/usr/bin/env python2
# encoding: utf-8
"""
A simple plugin framework.

The PluginManager will load all plugins of a given type in a given package and
provides methods for manageing them.

Plugins are responsible for determining weather or not they are enabled on
prepare and setting enabled appropriatly.

"""

__version__ = "0.1"
__author__ = "Steven Allen"
__email__ = "steven@stebalien.com"


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
        for loader, module_name, is_pkg in pkgutil.iter_modules(self.plugin_package.__path__):
            for name, plugin in loader.find_module(module_name).load_module(module_name).__dict__.iteritems():
                if isclass(plugin) and issubclass(plugin, self.base_class) and plugin is not self.base_class and name not in self:
                    instance =  plugin(**self.instance_arguments)
                    self[name] = instance
                    self.on_load_plugin(instance)
    
    @property
    def enabled_plugins(self):
        """A list of the names of enabled plugins."""
        return [ p for p in self if p.enabled ]

    @property
    def disabled_plugins(self):
        """A list of the names of disabled plugins."""
        return [ p for p in self if p.disabled ]

    def enable_plugin(self, plugin):
        """ Enable a plugin

        Arguments:
            plugin - the plugin to enable
        """
        if self.plugins[plugin].enable():
            self.on_enable(plugin)

    def disable_plugin(self, plugin):
        """ Disable a plugin
        
        Arguments:
            plugin - the plugin to disable
        """
        if self.plugins[plugin].disable():
            self.on_disable(plugin)

    def on_enable_plugin(self, plugin):
        """Called when a plugin is enabled.

        Not called when a plugin is initially loaded.
        """
        pass

    def on_disable_plugin(self, plugin):
        """Called when a plugin is disabled."""
        pass

    def on_load_plugin(self, plugin):
        """Called when a plugin is loaded."""
        pass

class Plugin(object):

    def __init__(self):
        self.on_prepare()

    @property
    def enabled(self):
        """True if the plugin is enabled."""
        return getattr(self, "_enabled", False)
    @enabled.setter
    def enabled(self, value):
        if value != self.enabled:
            self._enabled = value
            if value:
                self.on_enable()
            else:
                self.on_disable()

    def enable(self):
        """Enable the plugin."""
        if not self.enabled:
            self.enabled = True
            return True
        return False

    def disable(self):
        """Disable the plugin."""
        if self.enabled:
            self.enabled = False
            return True
        return False

    def on_prepare(self):
        """Called when the plugin is loaded."""
        pass

    def on_enable(self):
        """Called when the plugin is enabled."""
        pass

    def on_disable(self):
        """Called when the plugin is disabled."""
        pass



import logging
import sys

from pathlib import Path
from typing import Any, Type

from errbot.plugin_info import PluginInfo
from .utils import collect_roots

log = logging.getLogger(__name__)


class PluginNotFoundException(Exception):
    pass


class BackendPluginManager:
    """
    This is a one shot plugin manager for Backends and Storage plugins.
    """
    def __init__(self, bot_config, base_module: str, plugin_name: str, base_class: Type,
                 base_search_dir, extra_search_dirs=()):
        self._config = bot_config
        self._base_module = base_module
        self._base_class = base_class

        self.plugin_info = None
        all_plugins_paths = collect_roots((base_search_dir, extra_search_dirs))
        plugin_places = [Path(root) for root in all_plugins_paths]
        for path in plugin_places:
            plugfiles = path.glob('**/*.plug')
            for plugfile in plugfiles:
                plugin_info = PluginInfo.load(plugfile)
                if plugin_info.name == plugin_name:
                    self.plugin_info = plugin_info
                    return
        raise PluginNotFoundException('Could not find the plugin named %s in %s.' % (plugin_name, all_plugins_paths))

    def load_plugin(self) -> Any:
        plugin_path = self.plugin_info.location.parent
        if plugin_path not in sys.path:
            sys.path.append(plugin_path)
        plugin_classes = self.plugin_info.load_plugin_classes(self._base_module, self._base_class)
        if len(plugin_classes) != 1:
            raise PluginNotFoundException('Found more that one plugin for %s.' % self._base_class)

        _, clazz = plugin_classes[0]
        return clazz(self._config)

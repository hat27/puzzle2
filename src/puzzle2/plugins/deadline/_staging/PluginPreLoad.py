#!/usr/bin/env python3
import sys
from Deadline.Scripting import RepositoryUtils

def __main__():
    pluginConfig = RepositoryUtils.GetPluginConfig("puzzle2", None)
    for key in ("PuzzleDirectory", "TaskDirectory", "YamlDirectory"):
        directory = pluginConfig.GetConfigEntryWithDefault(key, None)
        if directory and directory not in sys.path:
            sys.path.append(directory)

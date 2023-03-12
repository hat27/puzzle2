# -*- coding: utf-8 -*-
import os
name = 'puzzle2'

version = '1.0.0'


private_build_requires = ['rezutil-1']

def commands():
    global env
    global this
    global request
    global expandvars
    
    environ = this._environ
    result = list(environ["any"].items())
    
    # Add request-specific environments
    for key, values in environ.items():
        if key not in request:
            continue
    
        result += list(values.items())
    
    for key, value in result:
        if isinstance(value, (tuple, list)):
            [env[key].append(expandvars(v)) for v in value]
        else:
            env[key] = expandvars(value)

timestamp = 1614861425

format_version = 2

_environ = {'any': {}}

env_list = ["PUZZLE_JOB_PATH"]

for env in env_list:
    if env in os.environ:
        _environ["any"][env] = os.environ[env]

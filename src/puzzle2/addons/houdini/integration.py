import os


def get_app_path(version: str = "", program_directory: str = None) -> str:
    """
    Resolve hython.exe for Houdini.
    Default path example:
      C:/Program Files/Side Effects Software/Houdini 20.0/bin/hython.exe
    """
    # Explicit override via environment variable takes precedence
    # Use PUZZLE_HYTHON_PATH to avoid collision with other tools' env names
    override = os.environ.get("PUZZLE_HYTHON_PATH")
    if override:
        return os.path.normpath(override)

    base = (program_directory or os.environ.get("PROGRAMFILES", "C:/Program Files")).replace("\\", "/")
    # Accept versions like "20.0" or "19.5"; caller provides exact folder postfix
    path = f"{base}/Side Effects Software/Houdini {version}/bin/hython.exe" if version else f"{base}/Side Effects Software/bin/hython.exe"
    return os.path.normpath(path)


def close_event():
    # Nothing specific to close for hython batch runs
    return True


def get_command(**kwargs):
    version = kwargs.get("version", "")
    script_path = kwargs.get("script_path", "")
    app_path = get_app_path(version, kwargs.get("program_directory"))
    if not app_path or not os.path.exists(app_path):
        return False

    if "launcher" in kwargs:
        # When launched by another launcher (e.g., rez), omit the app path here
        return f' "{script_path}"'
    else:
        return f'"{app_path}" "{script_path}"'

import glob
import os

def scan_plugin_directory():
    """
    Dynamically locates and registers all plugin modules within subdirectories.
    """
    root_path = os.path.dirname(__file__)
    search_pattern = os.path.join(root_path, "*", "*.py")
    detected_files = glob.glob(search_pattern)

    loaded_modules = []

    for file_path in detected_files:
        if os.path.isfile(file_path) and not file_path.endswith("__init__.py"):

            relative_path = file_path.replace(root_path, "")

            module_path = relative_path.replace(os.sep, ".")

            clean_module_name = module_path[:-3]
            
            loaded_modules.append(clean_module_name)

    return sorted(loaded_modules)

ALL_MODULES = scan_plugin_directory()
__all__ = ALL_MODULES + ["ALL_MODULES"]
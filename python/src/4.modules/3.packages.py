## 1.packages
'''
A directory is just a standard folder on your operating system, 
whereas a package is a directory that Python can "import" as a module.
You can use the import statement on a package, but you cannot import a standard directory.
Packages allow you to organize modules into a hierarchical "dotted" namespace (e.g., import my_package.my_module). 
'''
import python_versions.src.python_features.version_3_10
from python_versions import python_3_10


# 2. __init__.py
'''
A package is a directory that typically contains a special __init__.py file.
This file signals to the Python interpreter that the directory should be treated as an "import package".

In the simplest case, __init__.py can just be an empty file,
but it can also execute initialization code for the package or set the __all__ variable,
'''

# 3. Importing * from a package
'''
The import statement uses the following convention: 
if a package’s __init__.py code defines a list named __all__, 
it is taken to be the list of module names that should be imported when from package import * is encountered.
'''
__all__ = ["echo", "surround", "reverse"]
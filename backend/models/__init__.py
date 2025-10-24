# models package
# Import model modules relatively so importing the package registers the models

from . import auth, users, conversations, messages  # type: ignore[reportUnusedImport]
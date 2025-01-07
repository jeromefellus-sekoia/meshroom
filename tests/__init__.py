from unittest.mock import patch

patch("getpass.getpass", return_value="password")
patch("getpass.unix_getpass", return_value="password")

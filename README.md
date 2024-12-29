Pykgin
======

Pykgin is an API to use pkgin in Python program.

# This project is no longer maintained, but if you are willing to take over, we'd be happy to have you onboard!

Example
=======

```python
>>> from pykgin import Pykgin
>>> pykg = Pykgin()
>>> pykg.update()
>>> pykg.installed("wget")
False
>>> pykg.install("wget")
{'download_size': '0B', 'install_size': '2131K', 'packages': [{'version': '1.14nb1', 'name': 'wget'}]}
>>> pykg.installed("wget")
True
>>> pykg.remove("wget")
>>> pykg.installed("wget")
False
>>> pykg.requires("wget")
['/usr/pkg/lib/libidn.so.11', '/usr/lib/libz.so.1', '/usr/lib/libssl.so.10', '/usr/lib/libintl.so.1', '/usr/lib/libgcc_s.so.1', '/usr/lib/libdes.so.8', '/usr/lib/libcrypto.so.8', '/usr/lib/libc.so.
12', '/lib/libcrypt.so.1']
>>> pykg.provides("wget")
[]
>>> pykg.search("wget")
[{'state': None, 'version': '2.20', 'name': 'wgetpaste'}, {'state': None, 'version': '1.14nb1', 'name': 'wget'}]
>>> pykg.show_pkg_category("wget")
['net']
>>> pykg.show_deps("wget")
[{'version': '1.26', 'name': 'libidn'}]
```

and more...

# virtualenvconfig

Modifies pip for a virtualenv to prefer a custom abi tag. This is used to make it easy to install
compiled c++ packages like numpy and scipy that work for a given Digital Content Creation software
(DCC) like Maya, 3ds Max, Nuke, Houdini, etc.

## installing

Here is a example of creating a virtualenv designed to install wheels compatible with DCC's compiled
with Visual Studio 2015. Create the virtual environment and activate it.

```
$ virtualenv msvc2015_64
$ msvc2015_64\Scripts\activate
(python) $ pip install virtualenvconfig
```

## Setting the abi

You can specify the abi(s) that pip will try to download before the normal wheels. In this example pip
will try to download wheels with a abi of `vc2015`. If no matching package is found, it will try to
download wheels with a abi of `vc2010`. If no matching package is found, it will attempt to find a package
as pip normally does. Make sure to call python so you use the virtualenv's python, not the system python.

```
(python) $ cd msvc2015_64\lib\site-packages
(python) $ python virtualenvconfig.py --set-abi vc2015 --set-abi vc2010
```

## Activating

Up to this point, we haven't actually updated pip's behavior. We need to monkey patch pip so it respects
our custom abi settings. This is done by adding/updating sitecustomize.py. When python is being initialized
it will attempt to import `sitecustomize`. Any errors in this file being imported are suppressed.

This command will create sitecustomize.py
```
(python) $ virtualenvconfig.py --install
```
If sitecustomize.py already exists, you need to pass the `--overwrite` or `-o` argument

```
(python) $ python virtualenvconfig.py --install -o
```

This creates sitecustomize.py in the lib folder not the site-packages folder. This makes it so
the sitecustomize python script is only run when activating the virtualenv, not if the site-packages
directory is used without activating the virtualenv.

# Virtualenv setup at Blur

Blur creates a virtualenv for each required Microsoft Visual C++ compiled version required for
the DCC software's we need. For example to support Maya 2018/2019, 3ds Max 2018/19, houdini16.5/17
we create ``C:\blur\lib\msvc2015_64_qt5\{release}\python`` as a python 2.7 virtualenv. We then
activate and pip install all the packages we want access to in python for these DCC's. This
includes numpy/scipy compiled for msvc2010, and our custom PyQt and database code compiled with
msvc2015 to be compatible with the DCC's. Then as part of our startup scripts we insert
``C:\blur\lib\msvc2015_64_qt5\{release}\python\Lib\site-packages`` at the start of ``sys.path``
allowing the DCC to use the python modules installed there.

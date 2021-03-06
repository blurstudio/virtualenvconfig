import os
import sys
import logging
from distutils.sysconfig import get_python_lib

__version__ = "0.0.8"

# Configure logging, Use a special logger so this doesn't enable debug printing
# from pip and other modules.
logger = logging.getLogger("virtualenvconfig")
# This code is likely run by sitecustomize.py, this ends up importing the module
# twice. This check prevents doubling the text output of log messages.
first_run = not bool(logger.handlers)
if first_run:
    if os.environ.get("VIRTUALENVCONFIG_VERBOSE", "").lower() == "true":
        console = logging.StreamHandler()
        logger.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter("-VC- %(message)s")
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logger.addHandler(console)


def is_venv():
    """ Are we running in a virtualenv https://stackoverflow.com/a/42580137 """
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def abi_filename():
    """ If this file exists, it will be used by pip as the system abi.

    This text file should contain the required abi string.
    For example ``vc2010`` or ``vc2015``.

    This path is relative to the current python's site-packages folder, this
    allows you to use the virtualenvconfig as a editable package and still
    reference the correct abi for the current virtualenv.
    """
    return os.path.join(get_python_lib(), "virtualenvconfig.txt")


def customize_filename():
    """ Return the filename for python's sitecustomize.py filename in this virtualenv.

    Should be the lib folder of the virtualenv. Found using the os module file path.
    This is installed in the lib folder to ensure the sitecustomize python script is only
    run when the virtualenv is activated, not if the site-packages folder is used without
    activating the virtualenv.
    """
    return os.path.join(os.path.dirname(os.__file__), "sitecustomize.py")


def install_sitecustomize(overwrite):
    customize = customize_filename()
    command = "import virtualenvconfig"
    found = False

    if os.path.exists(customize):
        if not overwrite:
            print("File already exists. Use --overwrite to force a update.")
            print(customize)
            sys.exit(1)
        with open(customize, "r") as fle:
            for line in fle:
                if command in line:
                    found = True
    if not found:
        with open(customize, "a") as fle:
            # Append our code to the end of the file
            fle.write("\n{} # Customize python when its launched\n".format(command))
        print('Installed in "{}"'.format(customize))


def abi_bdist_wheel():
    """ Force setup.py to require the --abi argument.

    Example setup.py:
        import virtualenvconfig
        setup(
            ...,
            cmdclass={'bdist_wheel': virtualenvconfig.abi_bdist_wheel()},
        )

    Returns:
        abi_bdist_wheel class that adds a required --abi command line argument. This
        argument forces the abi tag for wheel builds to this value.
    """
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class abi_bdist_wheel(_bdist_wheel):
        # https://github.com/Yelp/dumb-init/blob/48db0c0d0ecb4598d1a6400710445b85d67616bf/setup.py#L11-L27
        # Copy user_options from _bdist_wheel and add our argument to the top
        user_options = _bdist_wheel.user_options[:]
        user_options.insert(0, ("abi=", "a", "Custom abi tag, required."))

        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            # Mark us as not a pure python package
            self.root_is_pure = False
            if self.abi is None:
                raise ValueError("Parameter --abi must be passed to build this wheel.")

        def initialize_options(self):
            _bdist_wheel.initialize_options(self)
            self.abi = None

        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            return python, self.abi, plat

    return abi_bdist_wheel


def parse_arguments():
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="Forces pip to try one or more custom abi strings before trying "
        "its standard options. This does not require any additional command line "
        "arguments for pip. You can force debug printing by setting the environment "
        "variable VIRTUALENVCONFIG_VERBOSE to True."
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Add/update a sitecustomize.py file to the python site-packages",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="If sitecustomize.py already exists, update it by adding "
        "``import virtualenvconfig`` to the end of the file.",
    )
    parser.add_argument(
        "--set-abi",
        action="append",
        help="Configure the abi that virtualenvconfig will make pip prefer. "
        'For example: "vc2010". You can pass this argument more than once to '
        "add more abi values processed in the order provided. This argument "
        "always resets the abi settings.",
    )
    parser.add_argument(
        "--clear-abi", action="store_true", help="Remove the abi override."
    )
    return parser.parse_args()


if __name__ == "__main__":
    if not is_venv():
        print("virtualenvconfig.py should only be run on a active virtualenv.")
        sys.exit(1)

    args = parse_arguments()

    if args.install:
        install_sitecustomize(args.overwrite)

    filename = abi_filename()
    if args.set_abi is not None:
        with open(filename, "w") as fle:
            for abi in args.set_abi:
                fle.write("{}\n".format(abi))
        print("Updated virtualenv abi to :{}".format(args.set_abi))
    if args.clear_abi:
        os.remove(filename)
        print("Removed virtualenv abi")

else:
    # Install abi patches for pip
    filename = abi_filename()
    if is_venv() and os.path.exists(filename):
        abi_overrides = [v.strip() for v in open(filename).read().strip().split("\n")]

        logger.debug('Inserting pip abi "{}"'.format(", ".join(abi_overrides)))
        import gorilla
        import pip._internal.index
        import pip._internal.pep425tags

        destinations = [
            # Note: get_supported was removed from index in pip 19.2
            pip._internal.index,
            pip._internal.pep425tags,
        ]

        try:
            # target_python was added in pip 19.2
            import pip._internal.models.target_python

            destinations.append(pip._internal.models.target_python)
        except ImportError:
            pass

        pip_version = int(pip.__version__.split('.', 1)[0])
        # The arguments/return of get_supported were changed in pip 20
        if pip_version < 20:

            def get_supported(
                versions=None, noarch=False, platform=None, impl=None, abi=None
            ):
                logger.debug("get_supported called pip {}".format(pip.__version__))
                # We're overwriting an existing function here,
                # preserve its original behavior.
                original = gorilla.get_original_attribute(
                    pip._internal.pep425tags, "get_supported"
                )
                rows = original(
                    versions=versions,
                    noarch=noarch,
                    platform=platform,
                    impl=impl,
                    abi=abi,
                )

                # Insert our abi at the top of the stack. preserving the order specified in the file
                for abi_override in reversed(abi_overrides):
                    row = (rows[0][0], abi_override, rows[0][2])
                    rows.insert(0, row)
                for row in rows:
                    logger.debug("  {}".format(row))

                return rows

        else:  # pip 20.0 +
            from pip._vendor.packaging import tags

            def get_supported(version=None, platform=None, impl=None, abi=None):
                logger.debug("get_supported called pip {}".format(pip.__version__))
                # We're overwriting an existing function here,
                # preserve its original behavior.
                original = gorilla.get_original_attribute(
                    pip._internal.pep425tags, "get_supported"
                )
                rows = original(version=version, platform=platform, impl=impl, abi=abi)

                # Insert our abi at the top of the stack. preserving the order specified in the file
                base_tag = rows[0]
                for abi_override in reversed(abi_overrides):
                    row = tags.Tag(
                        base_tag.interpreter, abi_override, base_tag.platform
                    )
                    rows.insert(0, row)
                for row in rows:
                    logger.debug("  {}".format(row))

                return rows

        settings = gorilla.Settings(allow_hit=True)
        for destination in destinations:
            patch = gorilla.Patch(
                destination, "get_supported", get_supported, settings=settings
            )
            gorilla.apply(patch)

import doctest
import glob
import io
import pkg_resources


def load_tests(loader, tests, pattern):
    import os.path
    from mbm.__main__ import main as _main

    def main(*a):
        try:
            import sys
            stdout, stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
            _main(list(a))
        except SystemExit:  # pragma: no cover
            pass
        finally:
            sys.stdout.seek(0)
            sys.stderr.seek(0)
            result = (sys.stdout.read().strip() + "\n" +
                      sys.stderr.read().strip())
            sys.stdout, sys.stderr = stdout, stderr
        print(result.strip())

    globs = {}
    globs.update({k: v for k, v in globals().items()})
    globs.update({k: v for k, v in locals().items()})
    pwd = os.path.dirname(__file__)
    for fn in glob.glob("{}/tests/*.md".format(pwd)):
        tests.addTests(doctest.DocFileSuite(
            fn, module_relative=False, globs=globs,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE))

    loader.discover(start_dir="{}/tests".format(pwd))
    return tests


__version__ = pkg_resources.get_distribution("mbm").version

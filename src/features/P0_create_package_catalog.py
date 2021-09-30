import os
import io
import subprocess
import copy
from datetime import datetime


def create_csv(data, date_now, logging, lts):
    logging.info("Writing results to file")
    try:
        csv_file_name = "C:/Users/nicol/Documents/GitHub/stackage-evolution/data/test/%s/packages-catalog-{date}.csv".format(
            date=date_now) % lts
        with open(csv_file_name, "w") as csv_file:
            csv_file.write("\n".join(data))
        logging.info("CSV file created")
        return csv_file_name
    except IOError:
        logging.exception("Error: There was an error creating the file")


def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def clean_utf8(path_file):
    file = io.open(path_file, 'r', encoding="utf-8")

    test = file.read()
    text = test.encode("ascii", "replace")
    text = text.decode()
    file.close()

    file = io.open(path_file, 'w', encoding="utf-8")
    file.write(text)
    file.close()


def create_package_catalog(path, date_now, logging, lts):
    _tmp_pkg_tuple_dirs = []
    logging.info("Processing package index with root {path}".format(path=path))
    for _, pkg_tuple, _ in walklevel(path, level=0):
        _tmp_pkg_tuple_dirs.extend(pkg_tuple)
        _tmp_pkg_tuple_dirs = map(lambda x: (
            x, os.path.join(path, x)), _tmp_pkg_tuple_dirs)

    pkg_dirs = []
    for pkg_tuple in _tmp_pkg_tuple_dirs:
        pkg_name, pkg_path = pkg_tuple
        for _, versions, _ in walklevel(pkg_path, level=0):
            new_tuple = copy.deepcopy(pkg_tuple + (versions,))
            pkg_dirs.append(new_tuple)
        logging.debug(pkg_tuple)
    total_pkgs = len(list(pkg_dirs))
    logging.info(
        "Total Packages for Analysis: {total}".format(total=total_pkgs))
    logging.info("Starting work at %s" % str(datetime.now()))

    package_catalog = list()
    for pkg in pkg_dirs:
        (name, pkg_path, name_version) = pkg
        cabal_file = os.path.join(pkg_path, name_version[0], name + ".cabal")
        logging.info("Starting work at {cabal_file}".format(
            cabal_file=cabal_file))
        clean_utf8(cabal_file)
        completed_process = subprocess.run(
            os.path.join(os.path.dirname(__file__),
                         '../parse/ParseCabal.exe'),
            input=cabal_file,
            capture_output=True,
            text=True,
            shell=True,
        )

        if completed_process.returncode == 0:
            package_catalog.append(completed_process.stdout)

    return create_csv(package_catalog, date_now, logging, lts)

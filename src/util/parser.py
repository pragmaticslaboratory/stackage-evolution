import argparse


def setup_command_line():
    parser = argparse.ArgumentParser(
        description='Generate a CSV file with package catalog')
    parser.add_argument(
        "index", help="Path to directory holding the uncompressed Hackage index")
    parser.add_argument(
        "-v", "--verbose", help="Set log level to DEBUG to increase output verbosity", action="store_true")
    parser.add_argument(
        "-q", "--quiet", help="Set log level to ERROR to decrease output verbosity", action="store_true")
    return parser


if __name__ == '__main__':
    setup_command_line()

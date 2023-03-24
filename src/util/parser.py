import argparse


def setup_command_line():
    parser = argparse.ArgumentParser(
        description='Generate a CSV file with package catalog')
    parser.add_argument(
        "-v", "--verbose", help="Set log level to DEBUG to increase output verbosity", action="store_true")
    parser.add_argument(
        "-q", "--quiet", help="Set log level to ERROR to decrease output verbosity", action="store_true")
    parser.add_argument(
        "--revised", help="Set the PATH  to make and save the DataFrames with revised Cabals", action='store_true', default=False)
    parser.add_argument("--wsl", help="Set the PATHS to use wsl ",
                        action='store_true', default=False)

    return parser


if __name__ == '__main__':
    setup_command_line()

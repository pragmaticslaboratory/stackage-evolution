import logging


def setup_log_level(args):
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
    return logging


if __name__ == '__main__':
    setup_log_level()

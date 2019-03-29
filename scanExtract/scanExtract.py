
import argparse
import sys

from ms2 import Ms2Scans

def main():
    parser = argparse.ArgumentParser(description='Get list of scan info from ms2 files.')

    parser.add_argument('-m', '--multipleMatch', default = 'first',
                        choices=['one_line', 'first', 'all'],
                        help = 'How should scans with more than 1 precursor charge be handled?')

    parser.add_argument('-o', '--ofname', default = 'scanTable.tsv', help = 'Output file name.')

    parser.add_argument('ms2_file', nargs = '+', help = '.ms2 file to read.')

    args = parser.parse_args()

    scans = Ms2Scans()
    for f in args.ms2_file:
        sys.stdout.write('Working on: {}...'.format(f))
        try:
            scans.read(f, multipleMatch = args.multipleMatch)
            sys.stdout.write(' Done!\n')
        except RuntimeError as e:
            sys.stderr.write('\nError reading {}:\n{}'.format(f, e))

    sys.stdout.write('Writing {}...'.format(args.ofname))
    scans.write(args.ofname)
    sys.stdout.write(' Done.\n')

if __name__ == '__main__':
    main()

"""
Script to normalise a HXL dataset.
David Megginson
October 2014

Expand all compact-disaggregated columns.
Strip columns without hashtags.
Strip leading and trailing whitespace from values.
Strip all but one pre-tag header row.

Command-line usage:

  python -m hxl.scripts.normalize < DATA_IN.csv > DATA_OUT.csv

Program usage:

  import sys
  from hxl.scripts.normalize import normalize

  normalize(sys.stdin, sys.stdout)

License: Public Domain
Documentation: http://hxlstandard.org
"""

import sys
import csv
import argparse
from hxl.parser import HXLReader

def normalize(input, output, showHeaders = False):
    """
    Normalize a HXL dataset
    """

    parser = HXLReader(input)
    writer = csv.writer(output)

    if (showHeaders):
        writer.writerow(parser.headers)
    writer.writerow(parser.tags)

    for row in parser:
        writer.writerow(row.values)

# If run as script
if __name__ == '__main__':

    # Command-line arguments
    parser = argparse.ArgumentParser(description = 'Normalize a HXL file.')
    parser.add_argument('-H', '--headers', help='Preserve text header row above HXL hashtags', action='store_const', const=True, default=False);
    parser.add_argument('infile', help='HXL file to read (if omitted, use standard input).', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', help='HXL file to write (if omitted, use standard output).', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    normalize(args.infile, args.outfile, args.headers)

# end

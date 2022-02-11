#!/usr/bin/env python3

import argparse
import subprocess
from gamutrf.utils import replace_ext, parse_filename


def make_procs_args(sample_filename):
    procs_args = []
    out_filename = sample_filename
    
    if sample_filename.endswith('.gz'):
        procs_args.append(['gunzip', '-c', sample_filename])
        out_filename = replace_ext(out_filename, '')
    elif sample_filename.endswith('.zst'):
        procs_args.append(['zstdcat', sample_filename])
        out_filename = replace_ext(out_filename, '')

    _, sample_rate = parse_filename(out_filename)
    out_filename = replace_ext(out_filename, 'raw')
    # TODO: parse sample format
    in_bits = 16
    in_format = 'signed-integer'
    sox_in = sample_filename
    if procs_args:
        sox_in = '-'
    procs_args.append(
        ['sox', '-t', 'raw', '-r', str(sample_rate), '-c', '1', '-b', str(in_bits),
         '-e', in_format, sox_in, '-e', 'float', out_filename])
    return procs_args


def run_procs(procs_args):
    procs = []
    for proc_args in procs_args:
        stdin = None
        if procs:
            stdin = procs[-1].stdout
        procs.append(subprocess.Popen(proc_args, stdout=subprocess.PIPE, stdin=stdin))
    for proc in procs[:-1]:
        if proc.stdout is not None:
            proc.stdout.close()
    procs[-1].communicate()


def main():
    parser = argparse.ArgumentParser(
        description='Convert (possibly compressed) sample recording to a complex float raw file (gnuradio style)')
    parser.add_argument('samplefile', default='', help='sample file to read')
    args = parser.parse_args()
    procs_args = make_procs_args(args.samplefile)
    run_procs(procs_args) 


if __name__ == '__main__':
    main()

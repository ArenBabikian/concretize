import argparse
import logging

def parse_args():
    parser = argparse.ArgumentParser(prog='concretize', description='CLI for the Concretize tool')
    approach_subcmd = parser.add_subparsers(title='approach subcommands', dest='approach', metavar='COMMAND')

    # Main Options
    main_opt = parser.add_argument_group('main options')
    main_opt.add_argument('-v', '--verbosity', type=int, choices=(0, 1, 2, 3), default=1,  help='verbosity level',)
    main_opt.add_argument('-n', '--num-of-runs', type=int, default=1, help='Number of runs')
    main_opt.add_argument('-t', '--timeout', type=int, default=60, help='Time limit in seconds')
    logging.warning("Fix the map integration")
    main_opt.add_argument('-m', '--map', default="maps/town02.xodr", help='path to map file')

    # Data Options
    data_opt = parser.add_argument_group('data options')
    data_opt.add_argument('-all', '--store-all-outcomes', action='store_true', help='Store only the best solution')
    # TODO add save path stuff

    # MHS Approch
    mhs_cmd = approach_subcmd.add_parser('mhs', help='Use the MHS approach')
    mhs_cmd.add_argument('-aggr', '--aggregation-strategy', choices=['one', 'categories', 'actors', 'importance', 'categImpo', 'none'], default='actors', help='Objective aggregation strategy')
    mhs_cmd.add_argument('-algo', '--algorithm-name', choices=['nsga2', 'ga', 'nsga3'], default='nsga2', help='Evolutionary algorithm to use')
    mhs_cmd.add_argument('-rt', '--restart-time', type=float, default=-1, help='Restart time for the evolutionary algorithm')
    mhs_cmd.add_argument('-hist', '--history', choices=['none', 'shallow', 'deep'], default='none', help='History option for the MHS approach')

    # Brute Approach
    brute_cmd = approach_subcmd.add_parser('brute', help='Use the brute force approach')
    
    # Reverse Approach
    # for now only statc, this would be quite complicated for dynamic
    inverse_cmd = approach_subcmd.add_parser('inverse', help='Derive abstract specification from concrete scenarios')

    # Positional Arguments
    parser.add_argument('specification', help='a Concretize file to run', metavar='FILE')

    args = parser.parse_args()

    return args

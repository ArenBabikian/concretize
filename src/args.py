import argparse
import logging

def parse_args():
    parser = argparse.ArgumentParser(prog='concretize', description='CLI for the Concretize tool')
    approach_subcmd = parser.add_subparsers(title='approach subcommands', dest='approach', metavar='COMMAND')

    # Main Options
    main_opt = parser.add_argument_group('main options')
    main_opt.add_argument('-v', '--verbosity', type=int, choices=(0, 1, 2, 3), default=1,  help='verbosity level',)
    main_opt.add_argument('-n', '--num-of-scenarios', type=int, default=1, help='Number of concrete scenarios to generate')
    main_opt.add_argument('-t', '--timeout', type=int, default=60, help='Time limit in seconds')
    main_opt.add_argument('-m', '--map', default="maps/town02.xodr", help='path to map file')

    # Data Options
    data_opt = parser.add_argument_group('data options')
    data_opt.add_argument('-o', '--output-directory', default=None, help='Path to save the outputs (statistics, diagrams, etc)')
    data_opt.add_argument('-all', '--store-all-outcomes', action='store_true', help='Store only the best solution')
    data_opt.add_argument('-s-stat', '--save-statistics-file', default=None, help='Path name for statistics file')


    # Visualisation Options
    vis_opt = parser.add_argument_group('visualisation options')
    vis_opt.add_argument('-v-diag', '--view-diagram', action='store_true', help='Pop up diagram')
    vis_opt.add_argument('-s-diag', '--save-diagram', action='store_true', help='Save the diagram')
    vis_opt.add_argument('-z', '--zoom-diagram', action='store_true', help='Zoom to junction, or to the actors')
    vis_opt.add_argument('-sh-act', '--hide-actors', action='store_true', help='Hide the actors in the visualization')
    vis_opt.add_argument('-sh-man', '--show-maneuvers', action='store_true', help='Highlight the assigned maneuver regions in the visualization')
    vis_opt.add_argument('-sh-expa', '--show-exact-paths', action='store_true', help='Show the assigned exact paths in the visualization')

    # MHS Approch
    mhs_cmd = approach_subcmd.add_parser('mhs', help='Use the MHS approach')
    mhs_cmd.add_argument('-aggr', '--aggregation-strategy', choices=['one', 'categories', 'actors', 'importance', 'categImpo', 'none'], default='actors', help='Objective aggregation strategy')
    mhs_cmd.add_argument('-algo', '--algorithm-name', choices=['nsga2', 'ga', 'nsga3'], default='nsga2', help='Evolutionary algorithm to use')
    mhs_cmd.add_argument('-rt', '--restart-time', type=float, default=-1, help='Restart time for the evolutionary algorithm')
    mhs_cmd.add_argument('-hist', '--history', choices=['none', 'shallow', 'deep'], default='none', help='History option for the MHS approach')
    mhs_cmd.add_argument('-nr', '--num-of-mhs-runs', type=float, default=-1, help='Number of MHS runs to perform')

    # Brute Approach
    complete_cmd = approach_subcmd.add_parser('complete', help='Use a rule-based approach to generate a set of scenarios with abstract completeness')
    complete_cmd.add_argument('-j', '--junction', type=str, help='Id of the junction where to perform search')
    
    # Reverse Approach
    # for now only statc, this would be quite complicated for dynamic
    inverse_cmd = approach_subcmd.add_parser('inverse', help='Derive abstract specification from concrete scenarios')

    # Positional Arguments
    parser.add_argument('specification', help='a Concretize file to run', metavar='FILE')

    args = parser.parse_args()

    return args

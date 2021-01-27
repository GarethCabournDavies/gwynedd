import lal
import numpy as np
import sys
# A list of available detectors in lalsuite
LAL_DETECTORS = [(d.frDetector.prefix, d.frDetector.name)
                   for d in lal.CachedDetectors]

LAL_DETECTORS_STRING = ', '.join([l[0] for l in LAL_DETECTORS])

def insert_detector_option_group(parser):
    """
    Adds the options used to call detector options in an
    parser as an argument group

    Parameters
    -----------
    parser : object
        ArgumentParser instance.
    """
    detector_options = parser.add_argument_group(
                          "Options to select the detector from the list of lalsuite detectors or to use a custom detector")
    detector_options.add_argument('--ifo', help='Detector prefix. Defines the detector from pre-defined list. Predefined detectors: ' + LAL_DETECTORS_STRING)
    detector_options.add_argument('--custom-detector', action='store_true', help="Flag to indicate that a custom detector is being used. Mutually exclusive of --ifo")
    detector_options.add_argument('--custom-detector-name', help='name of custom detector')
    detector_options.add_argument('--custom-detector-prefix', help='name of custom detector')
    detector_options.add_argument('--custom-detector-yangle', help='name of custom detector')
    detector_options.add_argument('--custom-detector-xangle', help='name of custom detector')
    detector_options.add_argument('--custom-detector-', help='name of custom detector')

def check_detector_option_group(args):
    """
    Once arguments have been parsed, check that the arguments are
    compatible.
    """
    # Check for mutually-exclusive detector options
    if args.ifo and args.custom_detector:
        raise argparse.ArgumentError("--ifos and custom detector options are mutually exclusive")

import lal
import numpy as np
import sys
from pycbc import detector as pycbc_det

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
                          "Options to select the detector from the list of "
                          "lalsuite detectors or to use a custom detector.")
    detector_options.add_argument('--ifo',
                                  help='Detector prefix. Defines the detector '
                                       'from pre-defined list in lal. '
                                       'Options: ' + LAL_DETECTORS_STRING)
    detector_options.add_argument('--custom-detector', action='store_true',
                                  help="Flag to indicate that a custom "
                                       "detector is being used. Mutually "
                                       "exclusive of --ifo")
    detector_options.add_argument('--custom-detector-prefix',
                                  help='Two-letter prefix of custom detector')
    detector_options.add_argument('--custom-detector-longitude', type=float,
                                  help='longitude of custom detector, radians')
    detector_options.add_argument('--custom-detector-latitude', type=float,
                                  help='latitude of custom detector, radians')
    detector_options.add_argument('--custom-detector-height',  type=float,
                                  default=0,
                                  help='height of custom detector. Default=0.')
    detector_options.add_argument('--custom-detector-yangle', type=float,
                                  default=0,
                                  help='Azimuthal angle of the y-arm (angle '
                                       'drawn from pointing north). Default=0')
    detector_options.add_argument('--custom-detector-xangle', type=float,
                                  help='xangle of custom detector. '
                                       'Default=right angle from yangle with '
                                       'right hand rule.')
    detector_options.add_argument('--detector-reference-time', type=float,
                                  help="Reference time for Earth's rotation.")

def check_detector_option_group(args):
    """
    Once arguments have been parsed, check that the arguments are
    compatible.
    """
    # Check for mutually-exclusive detector options
    if args.ifo and args.custom_detector:
        raise argparse.ArgumentError("--ifos and custom detector options are "
                                     "mutually exclusive")

    custom_required_arguments_str = ("If providing --custom-detector, need to "
        "provide --custom-detector-name, --custom-detector-prefix, "
        "--custom-detector-longitude and --custom-detector-latitude")

    # If using a custom detector, needs name, prefix, and location
    if args.custom_detector:
        if not (args.custom_detector_name and args.custom_detector_longitude and
                args.custom_detector_prefix and args.custom_detector_latitude):
            raise argparse.ArgumentError(custom_required_arguments_str)

def from_cli(args):
    """
    Define the detector object from the command line
    """
    if args.custom_detector:
        pycbc_det.add_detector_on_earth(args.custom_detector_prefix,
                                        args.custom_detector_longitude,
                                        args.custom_detector_latitude,
                                        yangle=args.custom_detector_yangle,
                                        xangle=args.custom_detector_xangle,
                                        height=args.custom_detector_height)
        det = pycbc_det.Detector(args.custom_detector_prefix,
                                 reference_time=args.detector_reference_time)
    else:
        det = pycbc_det.Detector(args.ifo,
                                 reference_time=args.detector_reference_time)
    return det

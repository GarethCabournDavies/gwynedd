# This is largely a copy of the pycbc strain module, but separating out the
# fake strain functionality from the real strain things
import pycbc
import logging
from pycbc.types import TimeSeries
import numpy as np
from pycbc import DYN_RANGE_FAC

def insert_fake_data_option_group(parser):
    """
    Add fake strain-related options to the parser object
    Parameters:
    -----------
    parser: ArgumentParser object

    """

    data_fake_strain_group = parser.add_argument_group("Basic fake data ",
                  "options for generating h(t). These will be the basis of "
                  "the data which is transformed for nonstaionarity or "
                  "glitches added.")

    # What times define the start/end of the data?
    data_fake_strain_group.add_argument("--gps-start-time", required=True,
                                        help="The gps start time of the data "
                                             "(integer seconds)", type=int)
    data_fake_strain_group.add_argument("--gps-end-time", required=True,
                                        help="The gps end time of the data "
                                             "(integer seconds)", type=int)

    # Define the generated Gaussian noise psd
    data_fake_strain_group.add_argument("--fake-strain",
                help="Name of model PSD for generating fake gaussian noise.",
                choices=pycbc.psd.get_lalsim_psd_list() + ['zeroNoise'])
    data_fake_strain_group.add_argument("--fake-strain-seed", type=int, default=0,
                help="Seed value for the generation of fake colored"
                     " gaussian noise")
    data_fake_strain_group.add_argument("--fake-strain-from-file",
                help="File containing ASD for generating fake noise from it.")
    data_fake_strain_group.add_argument("--fake-strain-flow",
                default=10.0, type=float,
                help="Low frequency cutoff of the fake strain")
    data_fake_strain_group.add_argument("--fake-strain-filter-duration",
                default=128.0, type=float,
                help="Duration in seconds of the fake data coloring filter")
    data_fake_strain_group.add_argument("--fake-strain-sample-rate",
                default=16384, type=float,
                help="Sample rate of the fake data generation (keep this the "
                     "same to get the same data at different sample rates)")
    return data_fake_strain_group

def insert_frame_file_output_group(parser):
    """
    Add strain-related options to the parser object.
    Parameters
    -----------
    parser : object
        OptionParser instance.
    gps_times : bool, optional
        Include ``--gps-start-time`` and ``--gps-end-time`` options. Default
        is True.
    """

    data_output_group = parser.add_argument_group("Options to define the "
                  "metadata of the data when it is output.")

    data_output_group.add_argument("--channel-name", type=str,
                   help="The output channel containing the 'strain' data.")
    data_output_group.add_argument("--detector", type=str,
                   help="Detector identifier to use in output frame files.")
    data_output_group.add_argument("--frame-type", type=str,
                   help="Frame type to use in output")
    data_output_group.add_argument('--output-sample-rate',
                   type=float, default=16384,
                   help="Sample rate to be output to the frame file")

    return data_output_group



def from_cli(args, dyn_range_fac=DYN_RANGE_FAC, precision=None, pad_data=8.):
    """Parses the CLI options related to strain data reading and conditioning.
    Parameters
    ----------
    args : object
        Result of parsing the CLI with OptionParser, or any object with the
        required attributes  (gps-start-time, gps-end-time, strain-high-pass,
        pad-data, sample-rate, (frame-cache or frame-files), channel-name,
        fake-strain, fake-strain-seed, fake-strain-from-file, gating_file).
    dyn_range_fac : {float, pycbc.DYN_RANGE_FAC}, optional
        A large constant to reduce the dynamic range of the strain.
        Default: 5.9029581035870565e+20 (DYN_RANGE_FAC from pycbc)
    precision : string
        Precision of the returned strain ('single' or 'double').
    inj_filter_rejector : InjFilterRejector instance; optional, default=None
        If given send the InjFilterRejector instance to the inject module so
        that it can store a reduced representation of injections if
        necessary.
    Returns
    -------
    strain : TimeSeries
        The time series containing the conditioned strain data.
    """
#    injector = InjectionSet.from_cli(args)

    logging.info("Generating Fake Strain")
    duration = args.gps_end_time - args.gps_start_time
    pdf = 1.0 / args.fake_strain_filter_duration
    fake_flow = args.fake_strain_flow
    sample_rate = args.fake_strain_sample_rate
    plen = int(sample_rate / pdf) // 2 + 1

    if args.fake_strain_from_file:
        logging.info("Reading ASD from file")
        strain_psd = pycbc.psd.from_txt(args.fake_strain_from_file,
                                        plen, pdf,
                                        fake_flow,
                                        is_asd_file=True)
    elif args.fake_strain != 'zeroNoise':
        logging.info("Making PSD for strain")
        strain_psd = pycbc.psd.from_string(args.fake_strain, plen, pdf,
                                           fake_flow)

    if args.fake_strain == 'zeroNoise':
        logging.info("Making zero-noise time series")
        strain = TimeSeries(pycbc.types.zeros(duration * sample_rate),
                            delta_t=1.0 / sample_rate,
                            epoch=args.gps_start_time)
    else:
        logging.info("Making colored noise")
        from pycbc.noise.reproduceable import colored_noise
        strain = colored_noise(strain_psd,
                               args.gps_start_time - pad_data,
                               args.gps_end_time + pad_data,
                               low_frequency_cutoff=fake_flow)

    ####### THIS IS WHERE GLITCH INJECTIONS WOULD BE INCLUDED

#    Keeping this as the 
#    if injector is not None:
#        logging.info("Applying injections")
#        injections = \
#            injector.apply(strain, args.channel_name[0:2],
#                           distance_scale=args.injection_scale_factor,
#                           injection_sample_rate=args.injection_sample_rate,
#                           inj_filter_rejector=inj_filter_rejector)


    if precision == None:
        pass
    elif precision == 'single':
        logging.info("Converting to float32")
        strain = (strain * dyn_range_fac).astype(pycbc.types.float32)
    elif precision == "double":
        logging.info("Converting to float64")
        strain = (strain * dyn_range_fac).astype(pycbc.types.float64)
    else:
        raise ValueError("Unrecognized precision {}".format(precision))

    if pad_data:
        logging.info("Remove Padding")
        start = int(pad_data * strain.sample_rate)
        end = int(len(strain) - strain.sample_rate * pad_data)
        strain = strain[start:end]

    return strain

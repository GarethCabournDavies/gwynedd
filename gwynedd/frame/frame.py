import lalframe
import lal
from pycbc.frame.frame import _fr_type_map

def write_frame(location, channels, timeseries, detector=None):
    """Write a list of time series to a single frame file.
    Parameters
    ----------
    location : string
        A frame filename.
    channels : string or list of strings
        Either a string that contains the channel name or a list of channel
        name strings.
    timeseries: TimeSeries
        A TimeSeries or list of TimeSeries, corresponding to the data to be
        written to the frame file for a given channel.
    detector: pycbc detector object
        The detector which is used in the frame output
    """
    # check if a single channel or a list of channels
    if type(channels) is list and type(timeseries) is list:
        channels = channels
        timeseries = timeseries
    else:
        channels = [channels]
        timeseries = [timeseries]

    # check that timeseries have the same start and end time
    gps_start_times = {series.start_time for series in timeseries}
    gps_end_times = {series.end_time for series in timeseries}
    if len(gps_start_times) != 1 or len(gps_end_times) != 1:
        raise ValueError("Start and end times of TimeSeries must be identical.")

    # check that start, end time, and duration are integers
    gps_start_time = gps_start_times.pop()
    gps_end_time = gps_end_times.pop()
    duration = int(gps_end_time - gps_start_time)
    if gps_start_time % 1 or gps_end_time % 1:
        raise ValueError("Start and end times of TimeSeries must be integer seconds.")

    # Try getting the detector flags from the lal frdetector name bits
    # N.B. some detectors do not follow this format, but ignore these for now
    if detector:
        try:
            uppername = detector.lal().frDetector.name.upper()
            detector_flags = eval("lal.%s_DETECTOR_BIT" % uppername)
        except AttributeError:
            detector_flags = lal.LALDETECTORTYPE_ABSENT

    # create frame
    frame = lalframe.FrameNew(epoch=gps_start_time, duration=duration,
                              project='', run=1, frnum=1,
                              detectorFlags=detector_flags)

    for i,tseries in enumerate(timeseries):
        # get data type
        for seriestype in _fr_type_map.keys():
            if _fr_type_map[seriestype][1] == tseries.dtype:
                create_series_func = _fr_type_map[seriestype][2]
                create_sequence_func = _fr_type_map[seriestype][4]
                add_series_func = _fr_type_map[seriestype][5]
                break

        # add time series to frame
        series = create_series_func(channels[i], tseries.start_time,
                       0, tseries.delta_t, lal.ADCCountUnit,
                       len(tseries.numpy()))
        series.data = create_sequence_func(len(tseries.numpy()))
        series.data.data = tseries.numpy()
        add_series_func(frame, series)

    # write frame
    lalframe.FrameWrite(frame, location)

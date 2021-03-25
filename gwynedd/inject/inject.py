"""
Define stuff for use in injecting glitches into data
"""
import h5py
import logging
from pycbc.inject import inject as inject
from pycbc.inject.inject import _XMLInjectionSet
from pycbc.inject import hdfinjtypes as PYCBCHDFINJTYPES
import gwynedd.glitches as glitches

class InjectionSet(object):
    def __init__(self, filelist, **kwds):
        self.injection_sets = []
        for filename in filelist:
            if filename.endswith(('.xml', '.xml.gz', '.xmlgz')):
                # Deal with xml files as signal injectors only
                self.injection_sets.append(_XMLInjectionSet(filename, **kwds))
            else:
                self.injection_sets.append(_HDFInjectionSet(filename, **kwds))

    @staticmethod
    def from_cli(args):
        """
        """
        # There is one injection option - the list of injection files
        # So return a list of InjectionSet objects from the filename option
        if args.injection_files is None:
            return None
        else:
            injection_sets = []
            for filename in args.injection_files:
                injection_sets.append(InjectionSet(filename))
            return injection_sets

# hdfinjtypes is a dictionary of all the different possible injections
# To make this, inherit all PyCBC injection types, 
hdfinjtypes = PYCBCHDFINJTYPES.copy()

# Then make a dictionary containing all of the gwynedd injection types
GWYNEDDHDFINJTYPES = {}

# And combine these into one dictionary
hdfinjtypes.update(GWYNEDDHDFINJTYPES)
       
# This is a copy of the get_hdf_injtype function from 
# https://github.com/gwastro/pycbc/blob/v1.18.0/pycbc/inject/inject.py#L998,
# but this uses the updated hdfinjtypes dictionary 
def get_hdf_injtype(sim_file):
    """Gets the HDFInjectionSet class to use with the given file.
    This looks for the ``injtype`` in the given file's top level ``attrs``. If
    that attribute isn't set, will throw an error`.
    Parameters
    ----------
    sim_file : str
        Name of the file. The file must already exist.
    Returns
    -------
    HDFInjectionSet :
        The type of HDFInjectionSet to use.
    """
    with h5py.File(sim_file, 'r') as fp:
            ftype = fp.attrs['injtype']
    try:
        return hdfinjtypes[ftype]
    except KeyError:
        # may get a key error if the file type was stored as unicode instead
        # of string; if so, try decoding it
        try:
            ftype = str(ftype.decode())
        except AttributeError:
            # not actually a byte error; passing will reraise the KeyError
            pass
        return hdfinjtypes[ftype]

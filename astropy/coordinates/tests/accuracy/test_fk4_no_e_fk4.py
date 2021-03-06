# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import numpy as np

from .... import units as u
from ...builtin_frames import FK4NoETerms, FK4
from ....time import Time
from ....table import Table
from ...angle_utilities import angular_separation
from ....utils.data import get_pkg_data_contents
from ....extern.six.moves import range

# the number of tests to run
from . import N_ACCURACY_TESTS

# It looks as though SLALIB, which AST relies on, assumes a simplified version
# of the e-terms corretion, so we have to up the tolerance a bit to get things
# to agree.
TOLERANCE = 1.e-5  # arcseconds


def test_fk4_no_e_fk4():
    lines = get_pkg_data_contents('fk4_no_e_fk4.csv').split('\n')
    t = Table.read(lines, format='ascii', delimiter=',', guess=False)

    if N_ACCURACY_TESTS >= len(t):
        idxs = range(len(t))
    else:
        idxs = np.random.randint(len(t), size=N_ACCURACY_TESTS)

    diffarcsec1 = []
    diffarcsec2 = []
    for i in idxs:
        # Extract row
        r = t[int(i)]  # int here is to get around a py 3.x astropy.table bug

        # FK4 to FK4NoETerms
        c1 = FK4(ra=r['ra_in']*u.deg, dec=r['dec_in']*u.deg,
                 obstime=Time(r['obstime'], scale='utc'))
        c2 = c1.transform_to(FK4NoETerms)

        # Find difference
        diff = angular_separation(c2.ra.radian, c2.dec.radian,
                                  np.radians(r['ra_fk4ne']), np.radians(r['dec_fk4ne']))

        diffarcsec1.append(np.degrees(diff) * 3600.)

        # FK4NoETerms to FK4
        c1 = FK4NoETerms(ra=r['ra_in']*u.deg, dec=r['dec_in']*u.deg,
                         obstime=Time(r['obstime'], scale='utc'))
        c2 = c1.transform_to(FK4)

        # Find difference
        diff = angular_separation(c2.ra.radian, c2.dec.radian,
                                  np.radians(r['ra_fk4']),
                                  np.radians(r['dec_fk4']))

        diffarcsec2.append(np.degrees(diff) * 3600.)

    np.testing.assert_array_less(diffarcsec1, TOLERANCE)
    np.testing.assert_array_less(diffarcsec2, TOLERANCE)

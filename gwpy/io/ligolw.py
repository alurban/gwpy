# coding=utf-8
# Copyright (C) Duncan Macleod (2014)
#
# This file is part of GWpy.
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.

"""Basic utilities for reading/writing LIGO_LW-format XML files.

All specific unified input/output for class objecst should be placed in
an 'io' subdirectory of the containing directory for that class.
"""

from glue.lal import (Cache, CacheEntry)
from glue.ligolw.ligolw import (Document, LIGOLWContentHandler)
from glue.ligolw.utils.ligolw_add import ligolw_add
from glue.ligolw import (table, lsctables)

from .. import version
from .cache import file_list

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'
__version__ = version.version


class GWpyContentHandler(LIGOLWContentHandler):
    pass


def table_from_file(f, tablename, columns=None,
                    contenthandler=GWpyContentHandler, nproc=1):
    """Read a :class:`~glue.ligolw.table.Table` from a LIGO_LW file.

    Parameters
    ----------
    f : `file`, `str`, `CacheEntry`, `list`, `Cache`
        object representing one or more files. One of

        - an open `file`
        - a `str` pointing to a file path on disk
        - a formatted :class:`~glue.lal.CacheEntry` representing one file
        - a `list` of `str` file paths
        - a formatted :class:`~glue.lal.Cache` representing many files

    tablename : `str`
        name of the table to read.
    columns : `list`, optional
        list of column name strings to read, default all.
    contenthandler : :class:`~glue.ligolw.ligolw.LIGOLWContentHandler`
        SAX content handler for parsing LIGO_LW documents.

    Returns
    -------
    table : :class:`~glue.ligolw.table.Table`
        `Table` of data with given columns filled
    """
    # find table class
    tableclass = lsctables.TableByName[table.StripTableName(tablename)]

    # allow cache multiprocessing
    if nproc != 1:
        return tableclass.read(f, columns=columns,
                               contenthandler=contenthandler,
                               nproc=nproc, format='cache')

    # set columns to read
    if columns is not None:
        _oldcols = tableclass.loadcolumns
        tableclass.loadcolumns = columns

    # generate Document and populate
    xmldoc = Document()
    ligolw_add(xmldoc, file_list(f), non_lsc_tables_ok=True,
               contenthandler=contenthandler)

    # extract table
    out = tableclass.get_table(xmldoc)
    if columns is not None:
        tableclass.loadcolumns = _oldcols
    return out


def identify_ligolw_file(*args, **kwargs):
    """Determine an input object as either a LIGO_LW format file.
    """
    fp = args[3]
    if isinstance(fp, file):
        fp = fp.name
    elif isinstance(fp, CacheEntry):
        fp = fp.path
    # identify string
    if isinstance(fp, (unicode, str)) and fp.endswith(('xml', 'xml.gz')):
        return True
    else:
        return False
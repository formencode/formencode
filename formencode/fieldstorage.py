## FormEncode, a  Form processor
## Copyright (C) 2003, Ian Bicking <ianb@colorstudy.com>
##  
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 2.1 of the License, or (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with this library; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
## NOTE: In the context of the Python environment, I interpret "dynamic
## linking" as importing -- thus the LGPL applies to the contents of
## the modules, but make no requirements on code importing these
## modules.
"""
Wrapper class for use with cgi.FieldStorage types for file uploads
"""

import cgi

def convert_fieldstorage(fs):
    if fs.filename:
        return fs
    else:
        return None

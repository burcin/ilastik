# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Copyright 2011-2014, the ilastik developers

import inspect

def getRootArgSpec(f):
    if hasattr( f, '__wrapped__' ):
        return getRootArgSpec(f.__wrapped__)
    else:
        return inspect.getargspec(f)

class bind(tuple):
    """Behaves like functools.partial, but discards any extra
    parameters it gets when called. Also, bind objects can be compared
    for equality and hashed.

    bind objects are immutable.

    Inspired by boost::bind (C++).

    """
    def __new__(cls, f, *args):
        bound_args = args
        expected_args = getRootArgSpec(f).args
        numUnboundArgs = len(expected_args) - len(bound_args)
        if len(expected_args) > 0 and expected_args[0] == 'self':
            numUnboundArgs -= 1
        return tuple.__new__(cls, (f, bound_args, numUnboundArgs))

    @property
    def f(self):
        return self[0]

    @property
    def bound_args(self):
        return self[1]

    @property
    def numUnboundArgs(self):
        return self[2]

    def __call__(self, *args):
        """Execute the callback. If more args are provided than
        the callback accepts, silently discard the extra args.

        """
        self.f(*(self.bound_args + args[0:self.numUnboundArgs]))

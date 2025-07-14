..
    This file is part of listparser.
    Copyright 2009-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT

bozo_exception
==============

listparser should never propagate an exception to the software that called it;
instead it will store the exception in the ``bozo_exception`` key of the result it returns.
Developers may wish to check for exceptions, but it should not be a necessity.

.. seealso:: :doc:`bozo`

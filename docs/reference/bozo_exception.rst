bozo_exception
==============

listparser should never propogate an exception to the software that called it; instead it will store the exception in the ``bozo_exception`` key of the result it returns. Developers may wish to check for exceptions, but it should never be a necessity.

.. seealso:: :doc:`bozo`

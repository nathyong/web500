"""Actions upon stores in the web500 application, modelled as Python 3 Enums.
"""

from enum import Enum

_make_enum_dict = lambda xs: {x: x.upper() for x in xs}
_actions = ['init',
            'new_user']

AppAction = Enum('AppAction',
                 _make_enum_dict(_actions))

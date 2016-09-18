# encoding: utf-8
import collections, curses

BaseMouse = collections.namedtuple("BaseMouse", ["x", "y", "button"])

class Mouse(BaseMouse):
    LEFT_CLICKED = curses.BUTTON1_CLICKED
    MIDDLE_CLICKED = curses.BUTTON2_CLICKED
    RIGHT_CLICKED = curses.BUTTON3_CLICKED

    @classmethod
    def get_current(cls):
        _, x, y, _, button = curses.getmouse()
        return cls(x, y, button)

    def match(self, m):
        return self.button | m

class Key(str):
    pass

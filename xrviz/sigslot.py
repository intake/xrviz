# Source: https://github.com/martindurant/dfviz/blob/master/dfviz/widget.py
class SigSlot(object):
    """Signal-slot mixin, for Panel event passing"""

    def __init__(self):
        self._sigs = {}
        self._map = {}

    def _register(self, widget, name, thing='value'):
        """Watch the given attribute of a widget and assign it a named event

        This is normally called at the time a widget is instantiated, in the
        class which owns it.

        Parameters
        ----------
        widget : pn.layout.Panel or None
            Widget to watch. If None, an anonymous signal not associated with
            any widget.
        name : str
            Name of this event
        thing : str
            Attribute of the given widget to watch
        """
        self._sigs[name] = {'widget': widget, 'callbacks': [], 'thing': thing}
        wn = "-".join([widget.name if widget is not None else "none", thing])
        self._map[wn] = name
        if widget is not None:
            widget.param.watch(self._signal, thing, onlychanged=True)

    @property
    def signals(self):
        """Known named signals of this class"""
        return list(self._sigs)

    def connect(self, name, callback):
        """Associate call back with given event

        The callback must be a function which takes the "new" value of the
        watched attribute as the only parameter. If the callback return False,
        this cancels any further processing of the given event.
        """
        self._sigs[name]['callbacks'].append(callback)

    def _signal(self, event):
        """This is called by a an action on a widget

        Tests can execute this method by directly changing the values of
        widget components.
        """
        wn = "-".join([event.obj.name, event.name])
#         print(wn, event)
        if wn in self._map and self._map[wn] in self._sigs:
            self._emit(self._map[wn], event.new)

    def _emit(self, sig, value=None):
        """An event happened, call its callbacks

        This method can be used in tests to simulate message passing without
        directly changing visual elements.
        """
        for callback in self._sigs[sig]['callbacks']:
            if callback(value) is False:
                break

    def show(self):
        self.panel.show()
# Source: https://github.com/martindurant/dfviz/blob/master/dfviz/widget.py
import contextlib
import logging

logger = logging.getLogger('dfviz')
logger.setLevel('DEBUG')


class SigSlot(object):
    """Signal-slot mixin, for Panel event passing
    Include this class in a widget manager's superclasses to be able to
    register events and callbacks on Panel widgets managed by that class.
    The method ``_register`` should be called as widgets are added, and external
    code should call ``connect`` to associate callbacks.
    """

    def __init__(self):
        self._ignoring_events = False
        self._sigs = {}
        self._map = {}

    def _clear(self):
        """Remove all registered events"""
        self._sigs.clear()
        self._map.clear()

    def _deregister(self, name):
        """Remove named event"""
        del self._sigs[name]  # explicitly stop watchers?
        wn = [k for k, v in self._map.items() if v == name][0]
        del self._map[wn]

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
        self._sigs[name] = {'widget': widget, 'callbacks': [], 'thing': thing,
                            'log': logging.DEBUG}
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
        Within an self.ignore_events context, nothing happens.
        Tests can execute this method by directly changing the values of
        widget components.
        """
        if not self._ignoring_events:
            wn = "-".join([event.obj.name, event.name])
            if wn in self._map and self._map[wn] in self._sigs:
                self._emit(self._map[wn], event.new)

    @contextlib.contextmanager
    def ignore_events(self):
        """Temporarily turn off events processing in this instance"""
        self._ignoring_events = True
        try:
            yield
        finally:
            self._ignoring_events = False

    def _emit(self, sig, value=None):
        """An event happened, call its callbacks
        This method can be used in tests to simulate message passing without
        directly changing visual elements.
        Calling of callbacks will halt whenever one returns False.
        """
        logger.log(self._sigs[sig]['log'], f"{sig}: {value}")
        for callback in self._sigs[sig]['callbacks']:
            if callback(value) is False:
                break

    def show(self):
        """Open a new browser tab and display this instance's interface"""
        self.panel.show()

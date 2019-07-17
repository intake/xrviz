import inspect
import panel as pn
from .compatibility import ccrs, has_cartopy


def convert_widget(source, target):
    """
    To convert a widget form one type to another having
    same name, value and option as source widget.
    The value of source widget changes upon change in value
    of target.

    Parameters
    ----------
    `source`: The widget to be converted.
    `target`: The type of widget to be generated.

    Example:
    ```
    discrete_slider = pn.widgets.DiscreteSlider(name='Discrete Slider',
                                                options=[2, 4, 8, 16, 32, 64],
                                                value=32)
    selector = convert_widget(discrete_slider,pn.widgets.Select())
    ```
    """
    target_w = target
    target_w.name = source.params.args[0].name
    target_w.options = source.params.args[0].options
    target_w.value = source.params.args[0].value

    def callback(*events):
        for event in events:
            if event.name == 'value':
                source.value = event.new

    target_w.param.watch(callback, ['value'], onlychanged=False)

    return target_w


def _is_coord(data, name):
    if name in list(data.coords):
        return name + " " + '\U0001F4C8'
    else:
        return name


def player_with_name_and_value(source):
    """
    source: pn.widgets.DiscretePlayer()
    target: consists of source player's name, value and player itself

    With pn.widgets.DiscretePlayer, we don't get name and
    value updates in textual form. This method is useful
    in case we want name and continuous value update.
    """
    mark = pn.pane.Markdown(f'{source.value}')

    def callback(*events):
        for event in events:
            if event.name == 'value':
                mark.object = str(event.new)

    source.param.watch(callback, ['value'], onlychanged=False)
    target = pn.Column(pn.Row(source.name, mark), source)
    return target


def is_float(a):
    # int, 'Nan', 'inf' and '-inf' are also float
    try:
        float(a)
        return True
    except:
        return False

if has_cartopy:
    def proj_params(proj):
        proj = getattr(ccrs, proj)
        params = inspect.getfullargspec(proj)
        out = {}
        if 'self' in params.args:
            params.args.remove('self')
        if len(params.args) and len(params.args) == len(params.defaults):
            for arg, val in zip(params.args, params.defaults):
                out.update({arg: val})
        return str(out)

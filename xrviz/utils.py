

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

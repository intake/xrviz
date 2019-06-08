

def convert_widget(source, target):
    target_w = target
    target_w.name = source.params.args[0].name
    target_w.options = source.params.args[0].options
    target_w.value = source.params.args[0].value

    def callback(*events):
        for event in events:
            if event.name == 'value':
                source.value = event.new

    target_w.param.watch(callback, ['options', 'value'], onlychanged=False)

    return target_w

from celery import Celery, group, chain

app = Celery('tasks')
app.config_from_object('celeryconfig')

def flat_sum(values):
    return sum(
        value
        if isinstance(value, (int, float))
        else flat_sum(value)
        for value in values
    )

@app.task(bind=True)
def test_canvas(self, action, level=0):
    print(f'{self.request.root_id!s:36} {self.request.parent_id!s:36} {self.request.id!s:36} test_custom_task level={level} {action!r}')
    if isinstance(action, (int, float)):
        return action
    elif isinstance(action, (list, tuple)):
        return flat_sum(action)
    elif isinstance(action, dict):
        if len(action) != 1:
            raise ValueError(f'ambiguous action {action}')
        for mode, args in action.items():
            if mode == 'chain':
                replace = chain(test_canvas.si(arg, level=level + 1) for arg in args)
            elif mode == 'group':
                replace = group(test_canvas.si(arg, level=level + 1) for arg in args)
            elif mode == 'chord':
                replace = group(test_canvas.si(arg, level=level + 1) for arg in args) | test_canvas.s(level=level + 1)
            else:
                raise ValueError(f'unknown mode {mode}')
            return self.replace(replace)
    else:
        raise ValueError(repr(action))

def build_canvas(action, level=0):
    if isinstance(action, (int, float, str, bool)):
        return test_canvas.si(action, level=level)
    elif isinstance(action, dict):
        if len(action) != 1:
            raise ValueError(f'ambiguous action {action}')
        for mode, args in action.items():
            if mode == 'chain':
                return chain(build_canvas(arg, level=level + 1) for arg in args)
            elif mode == 'group':
                return group(build_canvas(arg, level=level + 1) for arg in args)
            elif mode == 'chord':
                return group(build_canvas(arg, level=level + 1) for arg in args) | test_canvas.s(level=level + 1)
            else:
                raise ValueError(f'unknown mode {mode}')
    else:
        raise ValueError(repr(action))

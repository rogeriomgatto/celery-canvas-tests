import unittest

from celery.exceptions import TimeoutError

from tasks import test_canvas, build_canvas


SUCCESS = 'SUCCESS'
FAILED = 'FAILED'
TIMEOUT = 'TIMEOUT'
ERROR = 'ERROR'

def scenarios():
    for top_operator in ('chain', 'group', 'chord'):
        yield SUCCESS, {top_operator: [1, 2, 3]}
        yield FAILED, {top_operator: [1, 'err', 3]}
        for nested_operator in ('chain', 'group', 'chord'):
            yield SUCCESS, {top_operator: [1, {nested_operator: [1, 2, 3]}, 3]}
            yield FAILED, {top_operator: [1, {nested_operator: [1, 'err', 3]}, 3]}

def run_signature(sig):
    result = sig.apply_async()
    try:
        val = result.get(timeout=10)
        return SUCCESS, val
    except TimeoutError as e:
        result.forget()
        return TIMEOUT, str(e)
    except Exception as e:
        if result.failed():
            return FAILED, str(e)
        else:
            # if an exception was thrown, shouldn't failed() be True?
            return ERROR, str(e)

class TestCanvas(unittest.TestCase):
    def test_all_scenarios(self):
        for expected, scenario in scenarios():
            for mode, signature in [
                ('dynamic', test_canvas.s(scenario)),
                ('static', build_canvas(scenario)),
            ]:
                with self.subTest(mode=mode, scenario=repr(scenario)):
                    result, value = run_signature(signature)
                    self.assertEqual(
                        result, expected,
                        f'return value: {value}'
                    )

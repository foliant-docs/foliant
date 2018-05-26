import re
from subprocess import run


PYLINT_SCORE_THRESHOLD = 8.50


def test_pylint(capfd):
    run('pylint foliant', shell=True)
    score_pattern = re.compile(r'Your code has been rated at (?P<score>\d\.\d{2})/10.*')

    score_line = capfd.readouterr().out.strip().splitlines()[-1]
    score = float(score_pattern.match(score_line).group('score'))

    assert score >= PYLINT_SCORE_THRESHOLD

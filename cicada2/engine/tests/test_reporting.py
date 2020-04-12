import os

from cicada2.engine import reporting


def test_render_report():
    test_state = {
        'test-name': {
            'actions': {
                'POST0': {
                    'results': [
                        {
                            'status_code': 200
                        }
                    ],
                    'outputs': {
                        'index': [1, 2, 3]
                    }
                }
            },
            'asserts': {
                'EqualsRows0': [
                    {
                        'passed': False,
                        'actual': None,
                        'expected': None,
                        'description': 'Exception calling application: (psycopg2.errors.UndefinedTable) relation "my_members" does not exist\nLINE 1: select count(*) as cnt from my_members where name=\'jeff2\'\n                                    ^\n\n[SQL: select count(*) as cnt from my_members where name=\'jeff2\']\n(Background on this error at: http://sqlalche.me/e/f405)'
                    }
                ]
            },
            'summary': {
                'completed_cycles': 12,
                'remaining_asserts': ['foo']
            }
        }
    }

    control_report_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'templates'
    )

    report = reporting.render_report(state=test_state)

    with open(os.path.join(control_report_dir, 'test_report.md'), 'r') as control_report:
        assert control_report.read() == report

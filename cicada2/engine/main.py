from cicada2.engine.scheduling import run_tests


if __name__ == '__main__':
    tests_folder = './example_tests'
    tasks_type = 'docker'
    run_tests(tests_folder, tasks_type)

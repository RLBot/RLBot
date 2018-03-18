from integration_test.gather_data import gather_data
from integration_test.test_runner import run_all_tests

def main():
    gather_data()
    run_all_tests()

if __name__ == '__main__':
    main()

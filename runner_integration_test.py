from integration_test.gather_data import gather_data
from integration_test.all_tests import run_all_tests

def main():
    gather_data()  # Note: you can comment this out if you want to analyze a history.pb.bin
    run_all_tests()

if __name__ == '__main__':
    main()

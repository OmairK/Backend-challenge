import csv
import sys

from faker import Faker

FIELD_NAMES = ['first_name', 'last_name', 'address', 'email', 'age', 'company']

def create_csv(records):
    """
    Function which creates a csv file with dummy data
    """
    fake = Faker()
    with open('dummy.csv', 'w', newline='') as dummy_csv:
        
        csvwriter = csv.DictWriter(dummy_csv, fieldnames=FIELD_NAMES)
        csvwriter.writeheader()
        for i in range(records):
            csvwriter.writerow({
                'first_name': fake.name(),
                'last_name': fake.name(),
                'address': fake.street_address(),
                'age': fake.random_number(fix_len=True,digits=2),
                'email': fake.email(),
                'company': fake.company()
            })
    
    print ('File creation complete')


if __name__ == '__main__':
    if (len(sys.argv) > 1):
        create_csv(int(sys.argv[1]))
    else:
        create_csv(200000)
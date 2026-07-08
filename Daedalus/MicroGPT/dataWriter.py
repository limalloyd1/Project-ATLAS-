import random 

numValues = 32000
filename = "numbers.txt"


def generate_us_phone():
    '''Generate a random US number'''
    area_code = random.randint(200, 999)
    exchange = random.randint(200, 999)
    subscriber = random.randint(1000, 9999)

    return f"({area_code}){exchange}-{subscriber}"


def main():
    print(f"Generating {numValues} numbers")
    numbers = [generate_us_phone() for i in range(numValues)]

    try:
        outfile = open(filename, 'w')
        outfile.write("\n".join(numbers))
    except Exception as e:
        print(f"An error occured: {e}")

    print("Done! Successfully wrote numbers to file!")


if __name__ == "__main__":
    main()

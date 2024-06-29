
def main():
    print('hello world')

    sum_of_two_strings = add_two_strings("2", "5")
    print(sum_of_two_strings)

    sum_of_two_doubles = add_two_floats(1.2, 3.5)
    print(sum_of_two_doubles)


def add_two_strings(first, second) -> str:
    result:  int = int(first) + int(second)
    return str(result)


def add_two_floats(first, second):
    return float(first) + float(second)


if __name__ == "__main__":
    main()





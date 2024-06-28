
def main():
    print('hello world')

    sum_of_two_strings = sum_two_strings("2", "5")
    print(sum_of_two_strings)

    sum_of_two_doubles = add_two_doubles(1.2, 3.5)
    print(sum_of_two_doubles)


def sum_two_strings(first, second):
    sum = int(first) + int(second)
    return sum


def add_two_doubles(first, second):
    sum = first + second
    return sum


if __name__ == "__main__":
    main()





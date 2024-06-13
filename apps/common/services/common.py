import decimal


def format_number_readable(num):
    """Format number to be readable."""
    num = int(num)
    return "{:,}".format(num)


if __name__ == "__main__":
    print(format_number_readable(1000000))
    print(format_number_readable(1000000.02))
    print(format_number_readable(decimal.Decimal("1000000.02")))

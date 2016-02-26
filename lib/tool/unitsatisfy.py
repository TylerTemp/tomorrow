def unit_satisfy(b):
    if b < 1024:
        return b, 'B'

    appropriate_size = b
    units = ('B', 'KB', 'MB', 'GB', 'TB')
    index = 0

    while (appropriate_size >> 10) >= 1024 and index < len(units) - 2:
        appropriate_size >>= 10
        index += 1

    return (appropriate_size / 1024, units[index + 1])


if __name__ == '__main__':
    print(unit_satisfy(3))
    print(unit_satisfy(1025))
    print(unit_satisfy(3 * 1024 * 1024 + 5))
    print(unit_satisfy(3 * 1024 * 1024 * 2014 + 5))
    print(unit_satisfy(3 * 1024 * 1024 * 2014 * 2014 + 5))
    print(unit_satisfy(3 * 1024 * 1024 * 2014 * 2014 * 1024 + 5))

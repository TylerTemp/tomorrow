def unit_satisfy(b):
    appropriate_size = b
    appropriate_unit = 'B'
    units = ('B', 'KB', 'MB', 'GB', 'TB')
    index = 0

    while (appropriate_size >> 10) >= 1024 and index < len(units) - 1:
        appropriate_size >>= 10
        index += 1
    return (appropriate_size / 1024, units[index])

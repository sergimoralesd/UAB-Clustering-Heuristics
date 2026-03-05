def varint_size(n):
    """Returns the byte size of a Bitcoin varint encoding of n."""
    if n < 0xfd:
        return 1
    elif n <= 0xffff:
        return 3
    elif n <= 0xffffffff:
        return 5
    else:
        return 9
def same_output(values: list, addresses: list):
    """
    Attempt to identify the change output in a replacement chain.

    An output is considered the change if its value appears in every
    transaction version and differs from every output value in the next
    version (i.e. the value is unique to one output and shifts at each
    replacement step).

    Parameters
    ----------
    values : list
        Values of original and replacement transaction.
    addresses : list
        Values of original and replacement transaction.

    Returns
    -------
    out_n : bool
    address : str | None
    """
    address = None
    check = 0
    value = 0
    # breakpoint()
    for i,x in enumerate(values[0]):
        # An output value that does not appear in the next version
        # is a candidate for the change output
        if False not in [x != y for y in values[1]]:
            check += 1
            if value == 0:
                # Keep only the first candidate found
                value = x
                address = addresses[0][i]

    # The change is identified only if exactly one output shifts at every step
    if check == 1:
        return True, address

    else:
        # Chain does not match the requested output count
        return False, address
    
def different_output(values: list, addresses: list):
    """
    Identifies which outputs in the last transaction of a single RBF chain
    could be the change output, based on whether their value is new
    (i.e., did not appear in any previous transaction in the chain).

   Parameters
    ----------
    values : list
        Values of original and replacement transaction.
    addresses : list
        Values of original and replacement transaction.

    Returns
    -------
    out_n : bool
    address : str | None
    """

    # Collect all output values seen in previous versions of the transaction.
    # When the same value appears more than once in a transaction, the output
    # index is appended to make the key unique (e.g. "0.001_1").
    past_values = set()
    for value, address in zip(values[-1], addresses[-1]):
        key = str(value)
        if key in past_values:
            key = f"{value}_{address}"
        past_values.add(key)

    # Build a map of output keys for the final transaction and record which
    # values are new (not present in any earlier version). The same deduplication
    # logic applies: duplicate values within the final tx get the index suffix.
    output_values = {}
    new_value_keys = []

    for value, address in zip(values, addresses):
        key = str(value)
        if key in output_values:
            key = f"{value}_{address}"
        output_values[key] = x['address']
        if key not in past_values:
            new_value_keys.append(key)

    # Only return true if there is one candidate.
    if len(new_value_keys) == 1:
        return True, output_values[key]

    return False, None
def get_myocontrol_grasp(myocontrol_array, column_index, threshold=0.2):
    """
    Detect grasp using the specified column of the myocontrol array.
    Returns a binary mask where 1 indicates grasp.
    """
    if not isinstance(column_index, int):
        raise ValueError("Column index must be an integer")

    col = myocontrol_array[:, column_index]
    return (col > threshold).astype(int)



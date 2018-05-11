def clean_string(string):
    """Use this to consistently do everything that needs to be done to make file paths legit, whenever needed"""
    # Replace "/" with "_"
    newstring = "_".join(string.split("/"))
    return newstring

def process_rooms(df):
    """ Function that changes formatting of column from # beds # bath to (#, #) in a tuple

    parameters:
    df: dataframe where we want rooms changed

    returns: 
    None
    """
    for count, text in enumerate(df['rooms']):
        data_wanted = [int(text.split()[i]) for i in [0,2]]
        data_wanted = tuple(data_wanted)
        df.loc[count, 'rooms'] = data_wanted


def preprocess(df) -> None:
    """ Function that preprocesses the dataframe

    Parameters: 

    df: dataframe that needs to be preprocessed

    Returns:
    None
    """
    process_cost_text(df)
    process_rooms(df)

def process_cost_text(df) -> None:
    """ Function that removes leading words and dollar sign from cost_text to make it usable as a float

    parameters:
    df: dataframe where we want cost_text cleaned

    returns: None
    """
    for count, text in enumerate(df['cost_text']):
        data_wanted = text.split()[0]
        data_wanted = data_wanted[1:]
        if (',' in data_wanted):
            data_wanted = data_wanted.replace(',', '')
        df.loc[count, "cost_text"] = float(data_wanted)

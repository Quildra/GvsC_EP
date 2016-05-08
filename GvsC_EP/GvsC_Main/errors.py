ERROR_OK = 0
ERROR_NO_VIABLE_MATCHES = 1000
ERROR_NOT_ALL_RESULTS_IN = 1001

def error_lookup( error_value ):
    if error_value == ERROR_OK:
        return None
    elif error_value == ERROR_NO_VIABLE_MATCHES:
        return "Unable to generate any more viable matches between opponents."
    elif error_value == ERROR_NOT_ALL_RESULTS_IN:
        return "Not all matches complete. The following matches still need results submitted: <br>"
    else:
        return "Unknown Error (" + error_value + ")"
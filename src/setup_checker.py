from os.path import basename

SCRIPT_NAME = basename(__file__)  # name of the current script, for use in logging


def try_log_message(message, lvl="INFO"):
    try:
        from services import construct_log_message
        print(construct_log_message(SCRIPT_NAME, message, level=lvl) + "\n")
        return True
    except ImportError:
        message = "! --- Unable to access item from within 'services' module. --- !"
        linebreak = "-"*len(message)
        print("\n{0}\n{1}\n{0}\n".format(linebreak, message))
        print("\n-> Make sure you've marked the 'src' as the 'Sources Root'\n")
        print("\n"+linebreak+"\n")
        return False


def try_log_error(message):
    try_log_message(message, lvl="WARN")


def get_api_key_definitions():
    from src.services.secrets import API_KEYS
    keys = API_KEYS.keys()
    values = API_KEYS.values()
    for value in values:
        value.keys()
        value.values()
    if not all([API_KEYS, keys, values]):
        raise ValueError

    try_log_message("'API_KEYS' from services.secrets is present and correctly formatted.")


def make_sample_call_to_service():
    from src.services import Service
    sample_service = Service(logging=False)
    sample_service.make_request()


if __name__ == "__main__":

    # test availability of other functions by checking log method (which we'll use later)
    print("\nBeginning initial setup tests to ensure everything is set up properly... \n")
    setup_successful = try_log_message("Successfully established a connection to 'services' module.")

    # see if 'API_KEYS' is set up properly in 'src/services/secrets.py'
    try:
        get_api_key_definitions()
    except (ImportError, NameError, AttributeError, ValueError):
        try_log_error("Unable to access API_KEYS or it was formatted incorrectly! Please check that you've configured `secrets.py` correctly")
        setup_successful = False

    # try a basic call to google API to see if core service functionality is working and set up
    try:
        make_sample_call_to_service()
        try_log_message("Successfully made a dummy request to a sample service.")
    except (ImportError, NameError) as error:
        try_log_error("Unable to make a dummy request to a sample service! Please check validity of API_KEYS, internet connection, api_path")
        print(error)
        setup_successful = False

    # log the results of the tests to the end user
    print("="*150)
    if setup_successful:
        try_log_message("All initial tests have run successfully. You should be all set!")
        exit(0)
    else:
        print("There was an error in one or more parts of the setup. Please review the logs.")
        exit(1)

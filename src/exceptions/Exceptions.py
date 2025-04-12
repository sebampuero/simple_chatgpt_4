class UnsupportedDataTypeException(Exception):
    """
    Exception raised for unsupported websocket data types.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
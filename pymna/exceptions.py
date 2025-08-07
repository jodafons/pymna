
__all__ = [
    "InvalidElement", 
    "InvalidMethod",
    "ImpossibleSolution"
    ]

class InvalidElement(Exception):
    def __init__(self, message, errors):
        super(InvalidElement, self).__init__(message)
        self.errors=errors

class InvalidMethod(Exception):
    def __init__(self, message, errors):
        super(InvalidMethod, self).__init__(message)
        self.errors=errors

class ImpossibleSolution(Exception):
    def __init__(self, message, errors):
        super(ImpossibleSolution, self).__init__(message)
        self.errors=errors
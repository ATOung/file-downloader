class DirectLinkError(Exception):
    """When lxml failed to find direct link"""
    def __init__(self):
        self.message="Lxml failed to find direct link"
    def __str__(self):
        return self.message

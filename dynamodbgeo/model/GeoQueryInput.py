
"""
Class to define the required input fields as defined in DynamoDB queryInput interface
"""


class GeoQueryInput:
    def __init__(self, query_input_dict: dict = {}):
        self.QueryInput = query_input_dict

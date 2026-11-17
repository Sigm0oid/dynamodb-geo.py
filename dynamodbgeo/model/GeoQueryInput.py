
"""
Class to define the required input fields as defined in DynamoDB queryInput interface
"""


import copy


class GeoQueryInput:
    def __init__(self, query_input_dict: dict = None):
        self.QueryInput = copy.deepcopy(query_input_dict) if query_input_dict is not None else {}

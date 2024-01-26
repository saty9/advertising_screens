"""
As custom forms can change order and structure this file provides methods to retrieve data from them using lists of
key value pairs and field names
"""

#  Copyright (c) 2020 Kyle Cooke.
#  All Rights Reserved


def make_search_chain(form_definition_id, form_section_id, form_element_id):
    return [
        ["custom_form_definition_id", form_definition_id],
        "custom_form_sections",
        ["custom_form_section_id", form_section_id],
        "custom_form_elements",
        ["custom_form_element_id", form_element_id],
        "custom_form_data_value"
    ]


search_chains = {
    #schedule form items
    'doors_time': make_search_chain(4, 0, 7),
    'end_time': make_search_chain(4, 0, 10),
}


def execute_chain(chain, custom_forms):
    out = custom_forms
    for expression in chain:
        if type(expression) is list:
            try:
                # get first item with key value pair matching expression
                out = next(filter(lambda item: item[expression[0]] == expression[1], out))
            except StopIteration:
                return None
        else:
            out = out[expression]

    return out

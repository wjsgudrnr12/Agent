from Processing.prompt_template import *

def get_query_context_prompt(query, context):
    return example_query_context_prompt.format(query, context)


def get_prompt(response):
    return example_prompt.format(response)

def get_func_call_prompt(query):
    return func_call_prompt.format(query.query)





def get_func_call_message(prompt):
    func_call_message = [

        {
            "role": "user",
            "content": prompt
        }
    ]
    return func_call_message

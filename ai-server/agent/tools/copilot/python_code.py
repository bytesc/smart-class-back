from .utils import call_llm_test

from .utils.parse_output import parse_generated_code


import logging
import pandas as pd
pd.set_option('display.max_columns', None)


def get_python_code_prompt(data, question):
    def slice_dfs(df_dict, lines=3):
        top_five_dict = {}
        for key, df in df_dict.items():
            top_five_dict[key] = df.head(min(lines, len(df)))
        return top_five_dict
    data_slice = slice_dfs(data)
    pre_prompt = """
    Write a Python function called draw_graph that takes only a pandas dataframe called data as input
    that performs the following operations:
    """

    data_prompt = """
    This data had already been selected and processed, you just need to draw graph based on the given data, 
    do not make any changes or calculation !!!.
    This data had already been selected and processed, you just need to draw graph based on the given data, 
    do not make any changes or calculation !!!.
    Here is the dataframe dict sample(it is just data structure samples not real data): 
    """

    end_prompt = """
    code should be completed in a single md code blocks without any comments, explanations or cmds.
    no comments no # no explanations no cmds.
    the function should not be called. do not print anything in the function.
    please import the module you need, modules must be imported inside the function.
    do not mock any data !!!
    """

    all_prompt = pre_prompt + question + "\n" + data_prompt + str(data_slice)

    all_prompt = all_prompt + "\n" + end_prompt

    return all_prompt


def get_py_code(data, question, llm, retries=3):
    final_prompt = get_python_code_prompt(data, question)
    retries_times = 0
    error_msg = ""
    while retries_times <= retries:
        retries_times += 1
        ans = call_llm_test.call_llm(final_prompt + error_msg, llm)
        ans_code = parse_generated_code(ans.content)
        if ans_code is not None:
            return ans_code
        else:
            error_msg = """code should only be in md code blocks: 
            ```python
                # some python code
            ```
            without any additional comments, explanations or cmds !!!"""
            logging.error(ans + "No code was generated.")
            print("No code was generated.")
            continue





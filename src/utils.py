import os
import re
import math
import json
import time
import openai
import backoff
import signal
import string
import func_timeout
import numpy as np
import sympy as sp
from sympy import solve, sympify, Symbol
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
    convert_xor


def extract_variables(content):
    content = content.split("```\n")[-1].split("\n```")[0]
    var_list = []
    for one_line in content.split('\n'):
        if '=' in one_line:
            one_var = one_line.split('=')[0].strip()
            continue
        else:
            one_var = one_line.split('#')[0].strip()
        if one_var != '':
            var_list.append(one_var)

    return var_list


def safe_execute(code_string: str, keys=None):
    def execute(x):
        try:
            exec(x)
            locals_ = locals()
            if keys is None:
                return locals_.get('ans', None)
            else:
                return [locals_.get(k, None) for k in keys]
        except Exception:
            return None

    try:
        ans = func_timeout.func_timeout(5, execute, args=(code_string,))
    except func_timeout.FunctionTimedOut:
        ans = None

    return ans


def safe_execute_func(code_string: str):
    def execute(x):
        try:
            exec(x)
            return eval('solution()')
        except Exception:
            return None

    try:
        ans = func_timeout.func_timeout(5, execute, args=(code_string,))
    except func_timeout.FunctionTimedOut:
        ans = None

    return ans


def timeout_exec(code):
    def execute(x):
        try:
            exec(x)
            return True
        except Exception:
            return None

    try:
        result = func_timeout.func_timeout(5, execute, args=(code,))
    except func_timeout.FunctionTimedOut:
        result = None
    except AssertionError:
        result = None
    except Exception as e:
        result = None

    return result


# ========================================
# ===== PoT related helper functions =====
# ========================================

def get_var_assign(code, method):
    var_assign = []
    for line in code.split('\n'):
        line = line.strip()
        if '=' not in line:
            continue
        rhs = line.split('=')[-1].strip()
        if method == 'pot' and rhs.isdigit():
            var_assign.append(line)
        elif method == 'eot' and (rhs.isdigit() or rhs == 'x'):
            var_assign.append(line)
    return var_assign


def handler(signum):
    raise TimeoutError(f"Exec Timeout: {signum}")


def get_stepwise_exec_results(code, method='pot'):
    """
    Get intermediate results by running step-by-step
    First safe execute and then get the results
    :return:
    """
    code_statements = code.split('\n')
    new_code_statements = []

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(5)
    # print(f"cand: {candidate_str}")
    try:
        exec(code)
        locals_ = locals()
    except Exception:
        locals_ = None

    signal.alarm(0)

    for statement in code_statements:
        try:
            if "=" in statement and statement.strip().split(' ')[0] != "ans":
                one_var = statement.strip().split("=")[0].strip()
                assert len(one_var.split(' ')) == 1
                if locals_ is not None:
                    one_value = round(locals_.get(one_var, None), 6)
                    new_statement = f"{one_var} = {one_value}"
                    new_code_statements.append(new_statement)
                else:
                    rhs = statement.split('=')[-1].strip()
                    if rhs.isdigit():
                        new_code_statements.append(statement)
        except Exception as e:
            continue

    return new_code_statements


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def get_chat_response(args, input, key, org_id, n=1):
    if org_id is not None:
        openai.organization = org_id
    patience = 100

    while patience > 0:
        patience -= 1
        try:
            if args.model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-0301', 'gpt-3.5-turbo-0613', 'gpt-4-0613']:
                response = openai.ChatCompletion.create(
                    model=args.model,
                    api_key=key,
                    messages=input,
                    temperature=args.temperature,
                    # max_tokens=args.max_tokens,
                    n=n
                )
                if n == 1:
                    prediction = response['choices'][0]['message']['content'].strip()
                    if prediction != "" and prediction != None:
                        return prediction
                else:
                    prediction = [choice['message']['content'].strip() for choice in response['choices']]
                    if prediction[0] != "" and prediction[0] != None:
                        return prediction
            else:
                completion_input = input[0]['content'] + '\n' + input[1]['content']
                response = openai.Completion.create(
                    engine=args.model,
                    api_key=key,
                    prompt=completion_input,
                    temperature=args.temperature,
                    max_tokens=1024,
                    n=n,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                    # stop="\n\n\n\n",
                )
                if n == 1:
                    prediction = response['choices'][0]['text'].strip()
                    if prediction != "" and prediction is not None:
                        return prediction
                else:
                    prediction = [choice['text'].strip() for choice in response['choices']]
                    if prediction[0] != "" and prediction[0] is not None:
                        return prediction

        except openai.error.RateLimitError:
            print('Rate limit error, waiting...')
            time.sleep(3)

        except openai.error.APIError:

            print('API error, waiting...')
            time.sleep(3)
        except openai.error.APIConnectionError:

            print('API Connection error, waiting...')
            time.sleep(3)

        except openai.error.Timeout:

            print('Timeout error, waiting...')
            time.sleep(3)

        except openai.error.ServiceUnavailableError:

            print('Service unavailable error, waiting...')
            time.sleep(3)
    return ""


def floatify_ans(ans):
    if ans is None:
        return None
    elif type(ans) == dict:
        ans = list(ans.values())[0]
    elif type(ans) == bool:
        ans = ans
    elif type(ans) in [list, tuple]:
        if not ans:
            return None
        else:
            try:
                ans = float(ans[0])
            except Exception:
                ans = str(ans[0])
    else:
        try:
            ans = float(ans)
        except Exception:
            ans = str(ans)
    return ans


def safe_solve_equation_system(equations):
    # pattern = r'^(\d+)([a-zA-Z])(?![0-9])'
    pattern = r'^([\d+\.]+)([a-zA-Z])'
    # digit_pattern = r'^([\d+\.]+)(\([\d+]+\))'  # 3(10) -> 3*10
    digit_pattern = r'^([\d+\.]+)\(([\d+]+)\)'

    def add_multiplication(match):
        return match.group(1) + '*' + match.group(2)

    def solve_equation_system(x):
        symbols = set()
        eqs = []
        for eq in x:
            # left, right = eq.replace('(', ' ( ').replace(')', ' ) ').split('=')
            # # parse_expr(sub_eqs, transformations=transformations)
            # left = [re.sub(pattern, add_multiplication, c) for c in left.strip().split()]
            # left = [re.sub(digit_pattern, add_multiplication, c) for c in left]
            # left = ' '.join(left)
            # right = [re.sub(pattern, add_multiplication, c) for c in right.strip().split()]
            # right = [re.sub(digit_pattern, add_multiplication, c) for c in right]
            # right = ' '.join(right)

            clean_eq = [re.sub(digit_pattern, add_multiplication, seg) for seg in eq.split()]
            clean_eq = ' '.join(clean_eq)
            left, right = clean_eq.replace('(', ' ( ').replace(')', ' ) ').split('=')
            # parse_expr(sub_eqs, transformations=transformations)
            left = [re.sub(pattern, add_multiplication, c) for c in left.strip().split()]
            left = ' '.join(left)

            right = [re.sub(pattern, add_multiplication, c) for c in right.strip().split()]
            right = ' '.join(right)

            eqs.append(sp.Eq(sp.sympify(left), sp.sympify(right)))
            symbols |= eqs[-1].free_symbols

        # print(eqs, symbols)
        solutions = sp.solve(eqs, symbols, dict=True)
        # print(solutions)
        return {str(k): v for k, v in solutions[0].items()}

    try:
        ans = func_timeout.func_timeout(5, solve_equation_system, args=(equations,))
    except func_timeout.FunctionTimedOut:
        ans = None

    return ans


def extract_code(response):
    r"""
    extract python function from model response: def solution() ... return xxx
    """
    response = response.split('def solution')[-1]
    response = response.split('### END ###')[0]
    response = 'def solution' + response.strip()
    code = []
    for line in response.split('\n'):
        code.append(line)
        if line.strip().startswith('return'):
            break
    return '\n'.join(code)


def chat_input_to_string(chat):
    chat_string = []
    for one_dict in chat:
        chat_string.append(f"{one_dict['role']}: {one_dict['content']}")
    return "\n".join(chat_string)


def get_final_using_sympy(equations):
    try:
        transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))
        if str(equations) == 'nan':
            return np.nan
        equation_list = equations.split(',')
        for eq in equation_list:
            for c in range(len(eq)):
                if c < len(eq) - 2:
                    if eq[c].isalpha() and eq[c + 1].isalpha() and eq[c + 2].isalpha():
                        return 'invalid equations'

        goal_var = None
        goal_expression_list = []

        if equation_list[-1].split('=')[0].strip().isalpha() or len(equation_list[-1].split('=')[0].strip()) == 2:
            goal_var = equation_list[-1].split('=')[0].strip()
        elif '=' in equation_list[-1]:
            for l in list(string.ascii_lowercase) + list(string.ascii_uppercase):
                if l not in equation_list[-1]:
                    goal_var = l
                    break
            if goal_var is not None:
                goal_expression = goal_var + ' - (' + equation_list[-1].split('=')[0].strip() + ')'
                goal_expression = parse_expr(goal_expression, transformations=transformations)
                goal_expression = sympify(goal_expression)
                try:
                    return float(solve(goal_expression)[0])
                except Exception as e:
                    pass
                goal_expression_list.append(goal_expression)
            else:
                return 'invalid equations'

        if len(equation_list) == 1:
            try:
                goal_expression = parse_expr(equation_list[0].split('=')[0], transformations=transformations)
                return float(sympify(goal_expression))
            except Exception as e:
                return 'invalid equations'

        if goal_var == None:
            return 'no goal found'

        for i in range(len(equation_list) - 1):
            sub_eqs = equation_list[i]
            if '?' not in sub_eqs:
                try:
                    sub_eqs_split = sub_eqs.split('=')
                    sub_eqs = sub_eqs_split[0].strip() + ' - (' + sub_eqs_split[1].strip() + ')'
                    sub_eqs = parse_expr(sub_eqs, transformations=transformations)
                    sub_eqs = sympify(sub_eqs)
                except Exception as e:
                    return 'invalid equations'
                goal_expression_list.append(sub_eqs)

                try:
                    try:
                        return float(solve(goal_expression_list)[Symbol(goal_var)])
                    except Exception as e:
                        return float(solve(goal_expression_list)[0][Symbol(goal_var)])
                except Exception as e:
                    pass

        return 'no solution'
    except Exception as e:
        print(e)
        return 'bug'


def sort_words_by_first_appearance(words, string):
    word_index = {}  # Store the first appearance index of each word

    for word in words:
        index = string.find(word)
        if index != -1:  # Word found in the string
            word_index[word] = index

    sorted_words = sorted(words, key=lambda x: word_index.get(x, float('inf')))
    return sorted_words


def extract_equations(response):
    try:
        eot_part = response.split("% System of linear equations:")[1]
        eq_flag = True
    except Exception as e:
        print(e)
        eot_part = response
        eq_flag = False

    equations = []

    for line in eot_part.splitlines():
        if eq_flag is False:
            if line.startswith("%"):
                eq_flag = True
            continue
        if not line.startswith("%") and '=' in line:
            equations.append(line.strip())
    return equations


if __name__ == '__main__':
    pass

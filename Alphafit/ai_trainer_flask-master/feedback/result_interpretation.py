import sys
from collections import Counter

import advice_messages

sys.path.append('feedback')


def advice(exercise, results):
    messages = advice_messages.messages[exercise]
    categories = advice_messages.messages[exercise + '_categories']

    major_problems = []
    minor_problems = []
    strengths = []

    try:
        # =====[ Iterate through each component  ]=====
        for key in results:
            num_reps = len(results[key])
            reps = (Counter(results[key])).most_common()

            # =====[ Iterate through each rep  ]=====
            for counts in reps:

                severity = float(counts[1]) / num_reps

                # =====[ Decide if label for rep indicates problem area  ]=====
                if counts[0] != 0:

                    # =====[ Decide if label for rep indicates major problem area  ]=====
                    if severity > 0.5:
                        major_problems.append(key)

                    elif severity > 0.25:
                        minor_problems.append(key)

                else:

                    # =====[ Decide if label indicates strong performance in category  ]=====
                    if severity > 0.9:
                        strengths.append(key)

        advice_map = {"reps": str(num_reps), "majorProblems": get_problems(major_problems, messages, categories, 'Major'),
                      "minorProblems": get_problems(minor_problems, messages, categories, 'Minor'),
                      "strengths": get_strengths(strengths, messages, categories),
                      "success": "true"}
    except TypeError:
        advice_map = {"success": "false"}
    return advice_map


def get_problems(problems, messages, categories, problem_type):
    result_list = []
    if len(problems) > 0:
        for problem in problems:
            result_list.append(categories[problem])
    return result_list


def get_strengths(strengths, messages, categories):
    result_list = []
    if len(strengths) > 0:
        for strength in strengths:
            result_list.append(categories[strength])
    return result_list


def print_problems(problems, messages, categories, problem_type):
    if len(problems) > 0:
        print('\n\n' + problem_type + ' Problems:\n')
        for problem in problems:
            print(categories[problem], ":", messages[problem])


def print_strengths(strengths, messages, categories):
    if len(strengths) > 0:
        print('\n\nStrengths:\n')
        for strength in strengths:
            print(categories[strength])

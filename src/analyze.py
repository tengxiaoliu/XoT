import os
import json
import time
import logging
import random
import argparse

from sklearn.metrics import confusion_matrix, accuracy_score
import numpy as np
from tabulate import tabulate
from collections import Counter

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default='', type=str)
    parser.add_argument("--cot", default='', type=str)
    parser.add_argument("--pot", default='', type=str)
    parser.add_argument("--eot", default='', type=str)
    parser.add_argument("--pot_assertion", default='', type=str)
    parser.add_argument("--eot_assertion", default='', type=str)
    parser.add_argument("--log_dir", default='outputs/logs', type=str)
    parser.add_argument("--tag", default='', type=str)

    random.seed(42)

    args = parser.parse_args()

    os.makedirs(args.log_dir, exist_ok=True)
    timestr = time.strftime("%m%d-%H%M%S")
    log_path = os.path.join(args.log_dir, f'{args.tag}_{timestr}.log')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create console handler and set level to INFO
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # Create file handler and set level to INFO
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(levelname)s - %(message)s')

    # Add formatter to handlers
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    dataset_paths = {
        'gsm': 'data/v8/gsm.jsonl',
        'algebra': 'data/raw/algebra/test.jsonl'
    }

    def load_result(path):
        instances = []
        with open(path, 'r') as f:
            for line in f.readlines():
                instances.append(json.loads(line.strip()))

        logger.info(f"Loaded {len(instances)} instances from {path}")
        return instances

    def total_acc(data):
        total = 0
        score_name = None
        for k in data[0].keys():
            if 'score' in k:
                score_name = k
                break

        for instance in data:
            total += instance[score_name]
        return total / len(data)

    cot_data = load_result(args.cot)
    pot_data = load_result(args.pot)
    eot_data = load_result(args.eot)
    pot_assertion_data = load_result(args.pot_assertion)
    eot_assertion_data = load_result(args.eot_assertion)
    if len(args.plan) > 0:
        plan_data = load_result(args.plan)
    else:
        plan_data = None

    data_len = len(cot_data)
    logger.info(f"Data length: {data_len}")
    assert data_len == len(pot_data) == len(eot_data) == len(pot_assertion_data), \
        f"Data length mismatch: {data_len} vs {len(pot_data)} vs {len(eot_data)} vs {len(pot_assertion_data)}"

    # ===== XoT performance =====
    cot_acc = total_acc(cot_data)
    pot_acc = total_acc(pot_data)
    eot_acc = total_acc(eot_data)

    logger.info(f"===== Single performance =====")
    logger.info(f"cot: {cot_acc}")
    logger.info(f"pot: {pot_acc}")
    logger.info(f"eot: {eot_acc}")

    # ===== XoT is good at =====
    pot_good = []
    cot_good = []
    eot_good = []

    for i in range(data_len):
        pot, cot, eot = pot_data[i], cot_data[i], eot_data[i]
        if pot['reason/pot/score'] == 1 and cot['reason/cot/score'] == 0 and eot['reason/eot/score'] == 0:
            pot_good.append(i)
        if pot['reason/pot/score'] == 0 and cot['reason/cot/score'] == 1 and eot['reason/eot/score'] == 0:
            cot_good.append(i)
        if pot['reason/pot/score'] == 0 and cot['reason/cot/score'] == 0 and eot['reason/eot/score'] == 1:
            eot_good.append(i)

    logger.info(f"===== XoT is good at =====")
    logger.info(f"cot: {len(cot_good)}")
    logger.info(f"pot: {len(pot_good)}")
    logger.info(f"eot: {len(eot_good)}")

    # ===== OR =====
    pot_or_eot = 0
    pot_or_cot = 0
    cot_or_eot = 0
    all_or = 0

    for i in range(data_len):
        pot, cot, eot = pot_data[i], cot_data[i], eot_data[i]
        pot_score, cot_score, eot_score = pot['reason/pot/score'], cot['reason/cot/score'], eot['reason/eot/score']

        if pot_score == 1 or eot_score == 1:
            pot_or_eot += 1
        if pot_score == 1 or cot_score == 1:
            pot_or_cot += 1
        if cot_score == 1 or eot_score == 1:
            cot_or_eot += 1
        if pot_score == 1 or cot_score == 1 or eot_score == 1:
            all_or += 1

    logger.info(f"===== OR =====")
    logger.info(f"pot or eot: {pot_or_eot}, {pot_or_eot / data_len}")
    logger.info(f"pot or cot: {pot_or_cot}, {pot_or_cot / data_len}")
    logger.info(f"cot or eot: {cot_or_eot}, {cot_or_eot / data_len}")
    logger.info(f"all or: {all_or}, {all_or / data_len}")

    # ===== Assertion confusion matrix =====
    def analyze_assertion(assertion_data, method='pot'):
        logger.info(f"===== Assertion confusion matrix: {method} =====")
        score1_check1 = 0
        score1_check0 = 0
        score0_check1 = 0
        score0_check0 = 0
        actual_labels = []
        predicted_labels = []
        
        for inst in assertion_data:
            score = inst[f'reason/{method}/score']
            flag = inst[f'think/check/{method}/flag']

            actual_labels.append(score)
            predicted_labels.append(flag)

            if score == 1 and flag == 1:
                score1_check1 += 1
            elif score == 1 and flag == 0:
                score1_check0 += 1
            elif score == 0 and flag == 1:
                score0_check1 += 1
            elif score == 0 and flag == 0:
                score0_check0 += 1

        logger.info(f"score1_check1: {score1_check1}")
        logger.info(f"score1_check0: {score1_check0}")
        logger.info(f"score0_check1: {score0_check1}")
        logger.info(f"score0_check0: {score0_check0}")

        # Confusion matrix
        actual_labels = np.array(actual_labels)
        predicted_labels = np.array(predicted_labels)
        cm = confusion_matrix(actual_labels, predicted_labels)

        accuracy = accuracy_score(actual_labels, predicted_labels)
        # Create a Markdown table
        table = tabulate(cm, headers=['Predicted 0', 'Predicted 1'], tablefmt='pipe')

        # Print confusion matrix in Markdown format
        logger.info("Confusion Matrix:")
        logger.info(table)
        logger.info(f"Accuracy: {accuracy}")
        logger.info(f"False Positive Rate: {cm[0][1] / (cm[0][1] + cm[0][0])}")
        logger.info(f"False Negative Rate: {cm[1][0] / (cm[1][0] + cm[1][1])}")

    analyze_assertion(pot_assertion_data, method='pot')
    analyze_assertion(eot_assertion_data, method='eot')


    def analyze_passive(xot_data, method='pot'):
        print(f"===== Passive confusion matrix: {method} =====")
        actual_labels = []
        predicted_labels = []

        for inst in xot_data:
            score = inst[f'reason/{method}/score']
            flag = 1 if inst[f'reason/{method}/ans'] is not None else 0

            actual_labels.append(score)
            predicted_labels.append(flag)

        # Confusion matrix
        actual_labels = np.array(actual_labels)
        predicted_labels = np.array(predicted_labels)
        cm = confusion_matrix(actual_labels, predicted_labels)
        accuracy = accuracy_score(actual_labels, predicted_labels)
        # Create a Markdown table
        table = tabulate(cm, headers=['Predicted 0', 'Predicted 1'], tablefmt='pipe')

        # Print confusion matrix in Markdown format
        logger.info("Confusion Matrix:")
        logger.info(table)
        logger.info(f"Accuracy: {accuracy}")
        logger.info(f"False Positive Rate: {cm[0][1] / (cm[0][1] + cm[0][0])}")
        logger.info(f"False Negative Rate: {cm[1][0] / (cm[1][0] + cm[1][1])}")

    analyze_passive(pot_data, method='pot')
    analyze_passive(eot_data, method='eot')

    # ===== Assert =====
    def xot_collaboration(xot1, xot2, assertion_data, method1, method2):
        collaborate_acc = 0
        for i in range(data_len):
            assert xot1[i]['id'] == xot2[i]['id']
            xot1_score = xot1[i][f'reason/{method1}/score']
            xot2_score = xot2[i][f'reason/{method2}/score']
            xot1_assert = assertion_data[i][f'think/check/{method1}/flag']
            if xot1_assert:
                collaborate_acc += xot1_score
            else:
                collaborate_acc += xot2_score
        logger.info(f"===== Assert {method1} & {method2} =====")
        logger.info(collaborate_acc / data_len)

    # only passive feedback
    def xot_collaboration_passive(xot1, xot2, method1, method2):
        collaborate_acc = 0
        for i in range(data_len):
            xot1_score = xot1[i][f'reason/{method1}/score']
            exec_ans = xot1[i][f'reason/{method1}/ans']
            xot2_score = xot2[i][f'reason/{method2}/score']
            if exec_ans is not None:
                collaborate_acc += xot1_score
            else:
                collaborate_acc += xot2_score
        logger.info(f"===== Passive {method1} & {method2} =====")
        logger.info(collaborate_acc / data_len)

    # pot assertion
    xot_collaboration(pot_data, eot_data, pot_assertion_data, 'pot', 'eot')
    xot_collaboration(pot_data, cot_data, pot_assertion_data, 'pot', 'cot')

    # eot assertion
    xot_collaboration(eot_data, pot_data, eot_assertion_data, 'eot', 'pot')
    xot_collaboration(eot_data, cot_data, eot_assertion_data, 'eot', 'cot')

    # passive feedbak
    xot_collaboration_passive(pot_data, cot_data, 'pot', 'cot')
    xot_collaboration_passive(eot_data, cot_data, 'eot', 'cot')

    # eot -> pot -> cot
    assert_eot_pot_cot_acc = 0
    for i in range(data_len):
        eot_score = eot_data[i]['reason/eot/score']
        pot_score = pot_data[i]['reason/pot/score']
        cot_score = cot_data[i]['reason/cot/score']
        pot_assert = pot_assertion_data[i]['think/check/pot/flag']
        eot_assert = eot_assertion_data[i]['think/check/eot/flag']
        if eot_assert:
            assert_eot_pot_cot_acc += eot_score
        elif pot_assert:
            assert_eot_pot_cot_acc += pot_score
        else:
            assert_eot_pot_cot_acc += cot_score
    logger.info(f"===== Assert eot & pot & cot =====")
    logger.info(assert_eot_pot_cot_acc / data_len)

    # pot -> eot -> cot
    assert_pot_eot_cot_acc = 0
    for i in range(data_len):
        eot_score = eot_data[i]['reason/eot/score']
        pot_score = pot_data[i]['reason/pot/score']
        cot_score = cot_data[i]['reason/cot/score']
        pot_assert = pot_assertion_data[i]['think/check/pot/flag']
        eot_assert = eot_assertion_data[i]['think/check/eot/flag']
        if pot_assert:
            assert_pot_eot_cot_acc += pot_score
        elif eot_assert:
            assert_pot_eot_cot_acc += eot_score
        else:
            assert_pot_eot_cot_acc += cot_score
    logger.info(f"===== Assert pot & eot & cot =====")
    logger.info(assert_pot_eot_cot_acc / data_len)

    logger.info(f"===== Majority Vote =====")
    sc_score = 0.0
    for i in range(data_len):
        eot_score = eot_data[i]['reason/eot/score']
        pot_score = pot_data[i]['reason/pot/score']
        cot_score = cot_data[i]['reason/cot/score']

        eot_ans = eot_data[i]['reason/eot/ans']
        pot_ans = pot_data[i]['reason/pot/ans']
        cot_ans = cot_data[i]['reason/cot/ans']

        # get the majority vote among three answers
        # Find the most frequent answer
        ans_list = [cot_ans, pot_ans, eot_ans]
        score_list = [cot_score, pot_score, eot_score]
        ans_list = [ans for ans in ans_list if ans is not None]

        one_sc = 0.0
        if len(ans_list) > 0:
            most_common = Counter(ans_list).most_common(1)[0]
            if most_common[1] == 1:
                sc_ans = random.sample(ans_list, 1)[0]
            else:
                sc_ans = most_common[0]

            # Retrieve the scores associated with the most frequent answer
            for answer, score in zip(ans_list, score_list):
                if answer == sc_ans:
                    one_sc = score
        sc_score += one_sc

    logger.info(sc_score / data_len)


    # ===== Plan =====
    if plan_data is not None:
        plan_pot_eot_acc = 0
        unknown_plan_cnt = 0
        plan_pot_idx = []
        plan_eot_idx = []
        for i in range(data_len):
            pot_score = pot_data[i]['reason/pot/score']
            eot_score = eot_data[i]['reason/eot/score']
            plan_method = plan_data[i]['plan']

            if 'equations' in plan_method:
                plan_pot_eot_acc += eot_score
                plan_eot_idx.append(i)
            elif 'Python' in plan_method:
                plan_pot_eot_acc += pot_score
                plan_pot_idx.append(i)
            else:
                plan_pot_eot_acc += pot_score
                plan_pot_idx.append(i)
                unknown_plan_cnt += 1
        logger.info(f"===== Plan PoT & EoT =====")
        logger.info(plan_pot_eot_acc / data_len)
        logger.info(f"Unknown plan method: {unknown_plan_cnt}")

        # ===== Plan pot_cot=====
        plan_pot_cot_acc = 0
        unknown_plan_cnt = 0
        plan_pot_idx = []
        plan_cot_idx = []
        for i in range(data_len):
            pot_score = pot_data[i]['reason/pot/score']
            cot_score = cot_data[i]['reason/cot/score']
            plan_method = plan_data[i]['plan']

            if 'equations' in plan_method:
                plan_pot_cot_acc += cot_score
                plan_cot_idx.append(i)
            elif 'Python' in plan_method:
                plan_pot_cot_acc += pot_score
                plan_pot_idx.append(i)
            else:
                plan_pot_cot_acc += pot_score
                plan_pot_idx.append(i)
                unknown_plan_cnt += 1
        logger.info(f"===== Plan PoT & CoT =====")
        logger.info(plan_pot_cot_acc / data_len)
        logger.info(f"Unknown plan method: {unknown_plan_cnt}")

        plan_pot_cnt = len(plan_pot_idx)
        plan_cot_cnt = len(plan_cot_idx)
        logger.info(f"Count PoT: {plan_pot_cnt} ({plan_pot_cnt /data_len}), CoT: {plan_cot_cnt} ({plan_cot_cnt / data_len})")



        # ===== Plan + assert + pe =====
        plan_assert_pe_acc = 0
        unknown_plan_cnt = 0
        for i in range(data_len):
            pot_score = pot_data[i]['reason/pot/score']
            eot_score = eot_data[i]['reason/eot/score']
            plan_method = plan_data[i]['plan']

            if 'equations' in plan_method:
                if eot_assertion_data[i]['think/check/eot/flag']:
                    plan_assert_pe_acc += eot_score
                else:
                    plan_assert_pe_acc += pot_score
            elif 'Python' in plan_method:
                if pot_assertion_data[i]['think/check/pot/flag']:
                    plan_assert_pe_acc += pot_score
                else:
                    plan_assert_pe_acc += eot_score
            else:
                if pot_assertion_data[i]['think/check/pot/flag']:
                    plan_assert_pe_acc += pot_score
                else:
                    plan_assert_pe_acc += eot_score

                unknown_plan_cnt += 1
        logger.info(f"===== Plan Assert PE =====")
        logger.info(plan_assert_pe_acc / data_len)
        logger.info(f"Unknown plan method: {unknown_plan_cnt}")

        # ===== Plan + passive =====
        plan_passive_acc = 0
        unknown_plan_cnt = 0
        steps_sum = 0
        for i in range(data_len):
            pot_score = pot_data[i]['reason/pot/score']
            eot_score = eot_data[i]['reason/eot/score']
            cot_score = cot_data[i]['reason/cot/score']
            plan_method = plan_data[i]['plan']

            if 'equations' in plan_method:
                if eot_data[i]['reason/eot/ans'] is not None:
                    plan_passive_acc += eot_score
                    steps_sum += 1
                elif pot_data[i]['reason/pot/ans'] is not None:
                    plan_passive_acc += pot_score
                    steps_sum += 2
                else:
                    plan_passive_acc += cot_score
                    steps_sum += 3
            elif 'Python' in plan_method:
                if pot_data[i]['reason/pot/ans'] is not None:
                    plan_passive_acc += pot_score
                    steps_sum += 1
                elif eot_data[i]['reason/eot/ans'] is not None:
                    plan_passive_acc += eot_score
                    steps_sum += 2
                else:
                    plan_passive_acc += cot_score
                    steps_sum += 3
            else:
                if pot_data[i]['reason/pot/ans'] is not None:
                    plan_passive_acc += pot_score
                    steps_sum += 1
                elif eot_data[i]['reason/eot/ans'] is not None:
                    plan_passive_acc += eot_score
                    steps_sum += 2
                else:
                    plan_passive_acc += cot_score
                    steps_sum += 3
                unknown_plan_cnt += 1
        logger.info(f"===== Plan Passive XoT =====")
        logger.info(plan_passive_acc / data_len)
        logger.info(f"Avg Steps: {steps_sum / data_len}")
        logger.info(f"Unknown plan method: {unknown_plan_cnt}")

        # ===== XoT main results: Plan + assert =====
        plan_assert_acc = 0
        unknown_plan_cnt = 0
        steps_sum = 0
        pec_cnt = {
            'p': 0, 'e': 0, 'c': 0
        }
        for i in range(data_len):
            pot_score = pot_data[i]['reason/pot/score']
            eot_score = eot_data[i]['reason/eot/score']
            cot_score = cot_data[i]['reason/cot/score']
            plan_method = plan_data[i]['plan']

            if 'equations' in plan_method:
                if eot_assertion_data[i]['think/check/eot/flag']:
                    plan_assert_acc += eot_score
                    steps_sum += 1
                    pec_cnt['e'] += 1
                elif pot_assertion_data[i]['think/check/pot/flag']:
                    plan_assert_acc += pot_score
                    steps_sum += 2
                    pec_cnt['p'] += 1
                else:
                    plan_assert_acc += cot_score
                    steps_sum += 3
                    pec_cnt['c'] += 1
            elif 'Python' in plan_method:
                if pot_assertion_data[i]['think/check/pot/flag']:
                    plan_assert_acc += pot_score
                    steps_sum += 1
                    pec_cnt['p'] += 1
                elif eot_assertion_data[i]['think/check/eot/flag']:
                    plan_assert_acc += eot_score
                    steps_sum += 2
                    pec_cnt['e'] += 1
                else:
                    plan_assert_acc += cot_score
                    steps_sum += 3
                    pec_cnt['c'] += 1
            else:
                if pot_assertion_data[i]['think/check/pot/flag']:
                    plan_assert_acc += pot_score
                    steps_sum += 1
                    pec_cnt['p'] += 1
                elif eot_assertion_data[i]['think/check/eot/flag']:
                    plan_assert_acc += eot_score
                    steps_sum += 2
                    pec_cnt['e'] += 1
                else:
                    plan_assert_acc += cot_score
                    steps_sum += 3
                    pec_cnt['c'] += 1
                unknown_plan_cnt += 1
        logger.info(f"===== XoT main results =====")
        logger.info(plan_assert_acc / data_len)
        logger.info(f"Avg Steps: {steps_sum / data_len}")
        logger.info(f"Unknown plan method: {unknown_plan_cnt}")
        logger.info(f"===== PEC ratio =====")
        logger.info(f"PoT: {pec_cnt['p']},{pec_cnt['p'] / data_len}, EoT: {pec_cnt['e']}, {pec_cnt['e'] / data_len},"
                    f"CoT: {pec_cnt['c']},{pec_cnt['c'] / data_len}")

    logger.info(f"Save results at {log_path}")

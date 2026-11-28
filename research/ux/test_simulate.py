import copy
import json
import unittest
from simulate import ROOT, validate_config, validate_completion, validate_result


class EvidenceContract(unittest.TestCase):
    def test_rejects_duplicate_input_ids(self):
        config = json.loads((ROOT / 'scenarios.json').read_text())
        for collection in ('controls', 'scenarios'):
            duplicate = copy.deepcopy(config)
            duplicate[collection].append(duplicate[collection][0])
            with self.subTest(collection=collection), self.assertRaises(ValueError):
                validate_config(duplicate)

    def test_rejects_missing_scenario_goal(self):
        config = json.loads((ROOT / 'scenarios.json').read_text())
        del config['scenarios'][0]['goal']
        with self.assertRaises(ValueError):
            validate_config(config)

    def test_rejects_truncated_completion(self):
        completion = {'model': 'resolved-model', 'choices': [{'finish_reason': 'length',
                      'message': {'content': '{"proposed_steps": [], "findings": []}'}}]}
        with self.assertRaises(ValueError):
            validate_completion(completion, set())
        completion['choices'][0]['finish_reason'] = 'stop'
        self.assertEqual(validate_completion(completion, set()), {'proposed_steps': [], 'findings': []})

    def test_rejects_invented_control(self):
        result = {'proposed_steps': ['尝试查找入口'], 'findings': [{
            'control_ids': ['invented'], 'friction': '不确定', 'frontend_need': '待验证',
            'backend_need': '待验证', 'validation_needed': '实际浏览器走查'}]}
        with self.assertRaises(ValueError):
            validate_result(result, {'sign-in'})

    def test_rejects_missing_validation(self):
        result = {'proposed_steps': [], 'findings': [{'control_ids': ['sign-in']}]}
        with self.assertRaises(ValueError):
            validate_result(result, {'sign-in'})

    def test_accepts_traceable_hypothesis(self):
        result = {'proposed_steps': ['查找入口（拟议）'], 'findings': [{
            'control_ids': ['sign-in'], 'friction': '可能不理解提供方',
            'frontend_need': '检验入口解释', 'backend_need': '检查失败码',
            'validation_needed': '使用测试账号记录真实登录结果'}]}
        self.assertEqual(validate_result(result, {'sign-in'}), result)


if __name__ == '__main__':
    unittest.main()

import unittest
import os
import sys

from puzzle2.PzTask import PzTask

module_path = os.path.normpath(os.path.join(__file__, "../../../"))
sys.path.append(module_path)

import tasks.win.mock as mock

class TaskFunctionTest(unittest.TestCase):
    def test_key_required(self):
        data = {}
        pz_task = PzTask(module=mock, data=data)
        response = pz_task.execute()
        self.assertEqual(response["return_code"], 5)

        data = {
            "name": "nameA"
        }
        pz_task = PzTask(module=mock, data=data)
        response = pz_task.execute()
        self.assertEqual(response["return_code"], 0)

    def test_data_key_replace(self):
        data = {"new_name": "nameB"}
        task = {"data_key_replace": {
                    "name": "new_name"
               }}
        
        pz_task = PzTask(module=mock, task=task, data=data)

        self.assertEqual(pz_task.data["name"], data["new_name"])

    def test_data_key_replace_from_other_task(self):
        data = {"name": "nameA"}
        task = {"data_key_replace": {
                    "name": "context.new_name"
               }}
        
        context = {"new_name": "nameB"}
        pz_task = PzTask(module=mock, task=task, data=data, context=context)
        self.assertEqual(pz_task.data["name"], context["new_name"])

    def test_conditions(self):
        data = {"name": "nameA", "category": "ch"}
        task = {"conditions": [{"category": "ch"}]}
        
        pz_task = PzTask(module=mock, task=task, data=data)
        self.assertEqual(pz_task.return_code, 0)

        data = {"name": "nameA", "category": "prop"}
        task = {"conditions": [{"category": "ch"}]}
        
        pz_task = PzTask(module=mock, task=task, data=data)
        self.assertEqual(pz_task.return_code, 2)

        data = {"name": "nameA", "category": "ch"}
        task = {"conditions": [{"category": "ch", "name": "nameA"}]}
        
        pz_task = PzTask(module=mock, task=task, data=data)
        self.assertEqual(pz_task.return_code, 0)


        data = {"name": "nameA", "category": "ch"}
        task = {"conditions": [{"category": "ch", "name": "nameB"}]}
        
        pz_task = PzTask(module=mock, task=task, data=data)
        self.assertEqual(pz_task.return_code, 2)


if __name__ == "__main__":
    unittest.main()



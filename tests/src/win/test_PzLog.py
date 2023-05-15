import unittest
import os
import sys
import logging


from puzzle2.PzLog import PzLog
import puzzle2.pz_config as pz_config
import unittest

class PzLogUseDefaultTemplate(unittest.TestCase):
    def setUp(self):
        """
        The 'reset_template' param always uses the default 'template.yml' file.
        """
        logging.Logger.manager.loggerDict.clear()
        self.pz_log = PzLog("test", reset_template=True)
    
    def test_check_template(self):
        self.assertEqual(os.path.basename(self.pz_log.base_template_path), "log.template.yml")
        for handler in self.pz_log.logger.handlers:
            if handler.name == "stream_handler":
                self.assertEqual(handler.level, logging.DEBUG)
    
    def tearDown(self):
        self.pz_log.remove_handlers()


class PzLogUseExistsTemplate(unittest.TestCase):
    def setUp(self):
        """
        create a default template logger.(pz_logA)
        then change level for next logger, with have same name.
        "new" param makes reflesh handlers.
        pz_logB will read template file from pz_logA's template file.
        but stream handler level will be changed to CRITICAL.
        """
        logging.Logger.manager.loggerDict.clear()

        self.pz_logA = PzLog("test2")
        info, config = pz_config.read(self.pz_logA.base_template_path)
        config["handlers"]["stream_handler"]["level"] = "CRITICAL"
        pz_config.save(self.pz_logA.base_template_path, config, {})

        self.pz_logB = PzLog("test2", new=True, reset_template=False)

    def test_check_template(self):
        """
        WARNING:
           in ths case, pz_logA's stream handler level will be changed to WARNING too.
           pz_logA and pz_logB have same logger object.
        """

        # check template file name.this is same as pz_logA's template file.
        self.assertEqual(os.path.basename(self.pz_logB.base_template_path), "test2.json")

        for handler in self.pz_logA.logger.handlers:
            if handler.name == "stream_handler":
                self.assertEqual(handler.level, logging.CRITICAL)

        for handler in self.pz_logB.logger.handlers:
            if handler.name == "stream_handler":
                self.assertEqual(handler.level, logging.CRITICAL)


class PzLogUseExistsTemplateAddingDateToLogName(unittest.TestCase):
    def setUp(self):
        """
        The "add_date_to_log_name" parameter creates a log file name that includes the date. 
        If the day changes, a different date log will be used, based on the existing template file. 
        In this case, the existing template file will not be used.
        """
        logging.Logger.manager.loggerDict.clear()
        self.pz_logA = PzLog("test3", add_date_to_log_name=True)
        self.pz_logB = PzLog("test3", new=True, reset_template=False, add_date_to_log_name=True)

    def test_check_template(self):
        """
        simmilier to PzLogUseExistsTemplate but add_date_to_log_name is True.
        so, default template.yml will be used.
        """
        self.assertEqual(os.path.basename(self.pz_logB.base_template_path), "log.template.yml")
        for handler in self.pz_logB.logger.handlers:
            if handler.name == "stream_handler":
                self.assertEqual(handler.level, logging.DEBUG)


class PzLogUtility(unittest.TestCase):
    def test_check_log_file_name(self):
        logging.Logger.manager.loggerDict.clear()
        self.pz_logA = PzLog("test1", add_date_to_log_name=True)
        import datetime
        now = datetime.datetime.now().strftime("%Y%m%d")
        for handler in self.pz_logA.logger.handlers:
            if handler.name == "file_handler":
                self.assertEqual(os.path.basename(handler.baseFilename), "{}_test1.log".format(now))

    def test_check_log_file_name02(self):
        logging.Logger.manager.loggerDict.clear()
        self.pz_logA = PzLog("test1", add_date_to_log_name=True, user_name="name")
        import datetime
        now = datetime.datetime.now().strftime("%Y%m%d")
        for handler in self.pz_logA.logger.handlers:
            if handler.name == "file_handler":
                self.assertEqual(os.path.basename(handler.baseFilename), "{}_test1_name.log".format(now))

    def test_update_level(self):
        logging.Logger.manager.loggerDict.clear()
        self.pz_logA = PzLog("test4", file_handler_level="CRITICAL", stream_handler_level="CRITICAL")

        for handler in self.pz_logA.logger.handlers:
            self.assertEqual(handler.level, logging.CRITICAL)
        

class PzLogDetail(unittest.TestCase):
    def setUp(self):
        self.pz_logA = PzLog("test5")
        self.logger = self.pz_logA.logger
    
    def test_add_details(self):
        self.logger.details.set_name("task_name1")
        name1 = self.logger.details.name

        self.logger.details.add_detail("test1")
        self.logger.details.add_detail("test2")
        self.logger.details.add_detail("test3")
        self.logger.details.set_header(0, "first task")

        self.logger.details.set_name("task_name2")
        name2 = self.logger.details.name
        self.logger.details.add_detail("test4")
        self.logger.details.add_detail("test5")
        self.logger.details.add_detail("test6")
        self.logger.details.set_header(1, "secound task")

        self.assertEqual(self.logger.details.get_details(name1), ["test1", "test2", "test3"])
        self.assertEqual(self.logger.details.get_details(name2), ["test4", "test5", "test6"])

        self.assertEqual(self.logger.details.get_details(), [["test1", "test2", "test3"], 
                                                             ["test4", "test5", "test6"]])

        self.assertEqual(self.logger.details.get_return_codes(), [0, 1])

        self.assertEqual(self.logger.details.get_all(), [{"return_code": 0, 
                                                          "header": "first task", 
                                                          "details": ["test1", "test2", "test3"], 
                                                          "meta_data": {}
                                                          },
                                                         {"return_code": 1, 
                                                          "header": "secound task", 
                                                          "details": ["test4", "test5", "test6"],
                                                          "meta_data": {}}
                                                          ])

        self.logger.details.clear()
       
        self.assertEqual(self.logger.details.get_header(), [])
        self.assertEqual(self.logger.details.get_details(), [])


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf8 -*-

import os
import sys
import time
import shutil
import unittest

module_path = os.path.normpath(os.path.join(__file__, "..\\..\\..\\"))

if module_path not in sys.path:
    sys.path.append(module_path)

sys.dont_write_bytecode = True

from puzzle2.PzLog import PzLog
import puzzle2.pz_env as pz_env


class PzLogTest(unittest.TestCase):
    def test_create_log_directory(self):
        log = PzLog()
        log_path = "C:/Users/{}/AppData/Local/Temp/Pzlog/log/unknown.log".format(os.environ["USERNAME"])
        config_path = "C:/Users/{}/AppData/Local/Temp/Pzlog/log/config/unknown.conf".format(os.environ["USERNAME"])
        self.assertEqual(log.log_path, log_path)
        self.assertEqual(log.config_path, config_path)
        self.assertEqual(os.path.exists(log.log_path), True)
        self.assertEqual(os.path.exists(log.config_path), True)

        log = PzLog(name="log_test")
        log_path = "C:/Users/{}/AppData/Local/Temp/Pzlog/log/log_test.log".format(os.environ["USERNAME"])
        config_path = "C:/Users/{}/AppData/Local/Temp/Pzlog/log/config/log_test.conf".format(os.environ["USERNAME"])

        self.assertEqual(log.log_path, log_path)
        self.assertEqual(log.config_path, config_path)
        self.assertEqual(os.path.exists(log.log_path), True)
        self.assertEqual(os.path.exists(log.config_path), True)

        log_directory = "{}_".format(pz_env.get_log_directory())
        log = PzLog(name="log_test", log_directory=log_directory)
        log_path = "C:/Users/{}/AppData/Local/Temp/puzzle/log_/log_test.log".format(os.environ["USERNAME"])
        config_path = "C:/Users/{}/AppData/Local/Temp/puzzle/log_/config/log_test.conf".format(os.environ["USERNAME"])

        self.assertEqual(log.log_path, log_path)
        self.assertEqual(log.config_path, config_path)
        self.assertEqual(os.path.exists(log.log_path), True)
        self.assertEqual(os.path.exists(log.config_path), True)

    def test_use_default_config(self):
        template = "{:04d}_{:02d}_{:02d}_{:02d}_{:02d}"
        log = PzLog()
        time.sleep(1)
        file_meta = time.localtime(os.stat(log.config_path).st_mtime)
        mtime = template.format(*file_meta)

        log2 = PzLog()
        time.sleep(1)
        file_meta = time.localtime(os.stat(log2.config_path).st_mtime)
        mtime2 = template.format(*file_meta)
        result = mtime == mtime2
        self.assertEqual(result, True)

        time.sleep(1)
        log3 = PzLog(use_default_config=True)

        file_meta = time.localtime(os.stat(log3.config_path).st_mtime)
        mtime3 = template.format(*file_meta)
        result = mtime == mtime3
        self.assertEqual(result, True)

    def test_check_save_file_name(self):
        log = PzLog()
        exists = False
        with open(log.config_path, "r") as f:
            f_s = f.read().split("\n")
            for l in f_s:
                if log.log_path in l:
                    exists = True
                    break

        self.assertEqual(exists, True)

    def test_change_level(self):
        log = PzLog()

        base_count = 0
        with open(log.log_path, "r") as f:
            base_count = len([line for line in f.read().split("\n") if line != ""])

        log.logger.debug("debug")

        against_count = 0
        with open(log.log_path, "r") as f:
            against_count = len([line for line in f.read().split("\n") if line != ""])

        self.assertEqual(against_count, base_count+1)

        log.remove_handlers()

        tmp = log.config_path.replace(".conf", "_.conf")
        shutil.copy2(log.config_path, tmp)
        with open(tmp, "r") as f:
            with open(log.config_path, "w") as new:
                f_s = f.read().split("\n")
                for l in f_s:
                    if "DEBUG" in l:
                        l = l.replace("DEBUG", "INFO")

                    new.write("{}\n".format(l))

        log = PzLog()
        log.logger.debug("debug")
        log.logger.debug("debug2")
        log.logger.debug("debug3")
        log.logger.info("info")

        result_count = 0
        with open(log.log_path, "r") as f:
            result_count = len([line for line in f.read().split("\n") if line != ""])


if __name__ == "__main__":
    unittest.main()
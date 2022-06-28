HOWTO

WARNING: 
develop branch only

cd puzzle2 directory

1. vertialenv
mkdir pipenv
cd pipenv
pipenv install --python 3.7
pipenv shell

3. install package
cd ../
pip install -e .

4. run test script
　python tests/win/test_normal_mode.py

5. unit test, check this file
  python tests/data/pieces/win/change_frame.py
  
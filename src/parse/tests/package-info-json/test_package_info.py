import json
import os
import re
import subprocess


def run_parser(case_path):
    path_list = [
        os.path.join(os.path.dirname(__file__), "inputs/test.cabal"),
        case_path,
    ]

    complated_process = subprocess.run(
        os.path.join(os.path.dirname(__file__), "../../PackageInfoJSON"),
        stdout=subprocess.PIPE,
        input="\n".join(path_list),
        text=True,
    )

    result = re.findall(r"(?=\{).+?(?<=\})", complated_process.stdout)
    return json.loads(result[0])["calls"]


def test_case1():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case1.txt")
    calls = run_parser(filename)

    assert "modify" in calls


def test_case2():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case2.txt")
    calls = run_parser(filename)

    assert "runState" in calls


def test_case3_1():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case3.txt")
    calls = run_parser(filename)

    assert "runState" in calls


def test_case3_2():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case3.txt")
    calls = run_parser(filename)

    assert "execStateT" in calls


def test_case4():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case4.txt")
    calls = run_parser(filename)

    assert "callCC" in calls


def test_case5():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case5.txt")
    calls = run_parser(filename)

    assert "runListT" in calls


def test_case6():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case6.txt")
    calls = run_parser(filename)

    assert "evalStateT" in calls


def test_case7():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case7.txt")
    calls = run_parser(filename)

    assert "evalState" in calls


def test_case8():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case8.txt")
    calls = run_parser(filename)

    assert "evalState" in calls

def test_case9():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case9.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case10():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case10.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case11():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case11.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case12():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case12.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls
    
def test_case13():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case13.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case14():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case14.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case15():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case15.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case16():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case16.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case17():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case17.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case18():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case18.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case19():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case19.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case20():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case20.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case21():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case21.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case22():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case22.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case23():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case23.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case24():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case24.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case25():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case25.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case26():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case26.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls

def test_case27():
    filename = os.path.join(os.path.dirname(__file__), "inputs/case27.txt")
    calls = run_parser(filename)    

    assert "evalState" in calls
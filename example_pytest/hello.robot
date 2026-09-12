*** Settings ***
Library    PytestRunner.py

*** Test Cases ***
Greeter Says Hello World
    [Documentation]    Verifies the greeter produces the correct greeting text.
    [Tags]    REQ-001    Greeting    Smoke
    Run Pytest Test    test_greeter.py::test_greeter_says_hello_world
    # Run Pytest Test    test_greeter.py::test_greeter_says_hello_world    requirement=REQ-001

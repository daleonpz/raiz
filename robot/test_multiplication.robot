*** Settings ***
Library    MathLibrary.py

*** Variables ***
${LOW}     0
${HIGH}    10

*** Test Cases ***
Multiply Integers
    [Documentation]    This test case verifies the multiplication of two integers.
    [Tags]    REQ-002   Multiply
    ${result}=    Multiply    2    5
    Should Be Equal As Integers     ${result}  10


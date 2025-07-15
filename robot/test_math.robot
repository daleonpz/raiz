*** Settings ***
Library    MathLibrary.py

*** Variables ***
${LOW}     0
${HIGH}    10

*** Test Cases ***
Add Integers
    [Documentation]    This test case verifies the addition of two integers.
    [Tags]    REQ-001   Add
    ${result}=    Add    3    4
    Should Be Equal As Integers   ${result}    7

Multiply Boundaries
    [Documentation]    This test case verifies the multiplication of boundary values.
    [Tags]    REQ-003   Multiply
    ${result}=    Multiply    ${LOW}    ${HIGH}
    Should Be Equal As Integers   ${result}    0


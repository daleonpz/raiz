*** Settings ***
Library    MathLibrary.py

*** Variables ***
${LOW}     0
${HIGH}    10

*** Test Cases ***
REQ-001 Add Integers
    ${result}=    Add    3    4
    Should Be Equal As Integers   ${result}    7

REQ-002 Multiply Integers
    ${result}=    Multiply    2    5
    Should Be Equal As Integers     ${result}  10

REQ-002 Multiply Boundaries
    ${result}=    Multiply    ${LOW}    ${HIGH}
    Should Be Equal As Integers   ${result}    0


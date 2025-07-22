*** Settings ***
Documentation    Sensor & orphan test case

*** Test Cases ***
Log Errors To Persistent SDCard
    [Tags]    REQ-002
    Log    Simulating SDCard logging

Sensor Sampling Adjustable
    [Tags]    REQ-003
    Log    Simulating sensor configuration

Encrypts Transmission Data
    [Tags]    REQ-004
    Log    Simulate encryption validation

Ghost Requirement Test
    [Tags]    REQ-999
    Log    This should point to a non-existing requirement

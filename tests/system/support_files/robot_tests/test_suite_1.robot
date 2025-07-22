*** Settings ***
Documentation    Tests covering BLE and Logging requirements
Test Tags        smoke

*** Test Cases ***
BLE Reconnects Quickly
    [Tags]    REQ-001
    Log    Simulating reconnect

BLE Reconnects Under Threshold
    [Tags]    REQ-001
    Log    More precise reconnect testing

Log Errors To Persistent Storage
    [Tags]    REQ-002
    Log    Simulating persistent logging

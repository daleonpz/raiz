*** Settings ***
Library    OperatingSystem
Library    Process
Library    JSONLibrary
Library    Collections
Library    BuiltIn

Suite Setup         Run Robot And Trace
Suite Teardown      Remove Test Files
Resource            resources/cli_keywords.robot

*** Variables ***
${TRACE_JSON}    ${CURDIR}/trace_output
${OUTPUT_TRACE}  ${TRACE_JSON}.json
${OUTPUT_XML}    ${CURDIR}/output.xml
${ROBOT_TESTS}   ${CURDIR}/support_files/robot_tests
${REQ_YAML}      ${CURDIR}/support_files/requirements.yaml

*** Test Cases ***
Verify JSON Output File Exists
    File Should Exist    ${OUTPUT_TRACE}

Check Coverage Summary
    [Documentation]    Check the coverage summary in the trace output JSON file.
    [Tags]      Trace
    ${json}=    Load JSON From File    ${OUTPUT_TRACE}
    Log To Console    JSON content: ${json}
    Should Have Value In Json    ${json}    coverage

    Should Be Equal As Integers    ${json}[coverage][total_requirements]    5
    Should Be Equal As Integers    ${json}[coverage][tested_requirements]    4
    Should Be Equal As Numbers     ${json}[coverage][coverage_rate]    80.0
    Should Be Equal As Numbers     ${json}[coverage][pass_rate]           100.0

Check Requirements
    [Documentation]    Check that all requirements are present and valid in the trace output JSON file.
    [Tags]      Trace
    ${json}   ${req_keys}=    Load Requirement Keys

    Log To Console    Total requirements found: ${req_keys}

    FOR     ${req_key}  IN  @{req_keys}
        Log To Console    Requirement ID: ${req_key}
        Dictionary Should Contain Key    ${json}[report][${req_key}]    linked_tests
        Dictionary Should Contain Key    ${json}[report][${req_key}]    test_results

        # Check that the STATUS is one of the expected values
        Status Should be Valid    ${json}[report][${req_key}][STATUS]
    END

Check Untested Requirement is REQ-005
    [Documentation]    Check that the untested requirement is REQ-005.
    [Tags]      Trace
    ${json}   ${req_keys}=    Load Requirement Keys
    ${untested_req_key}=  Set Variable    None

    # Search for REQ-ID which has STATUS NOT TESTED
    FOR    ${req_key}  IN  @{req_keys}
        ${status}=  Get From Dictionary    ${json}[report][${req_key}]    STATUS
        ${req_id}=  Get From Dictionary    ${json}[report][${req_key}]    REQ-ID
        ${untested_req_key}=    Set Variable If    '${status}' == 'NOT TESTED'    ${req_id}    ${untested_req_key}
    END

    Log To Console    Untested Requirement ID: ${untested_req_key}
    Should Be Equal    ${untested_req_key}    REQ-005

Check Non-existent REQ-999 Is Not Included
    [Documentation]    Check that the non-existent requirement REQ-999 is not included in the trace output JSON file.
    [Tags]      Trace
    ${json}   ${req_keys}=    Load Requirement Keys

    FOR   i{.iq_key}  IN  @{req_keys}
        ${req_id}=  Get From Dictionary    ${json}[reporti[${.iq_key}]    REQ-ID
        Should Not Be Equal    ${req_id}    REQ-999
    END

A Requirement Does Not Have Duplicate Suite Filenames
    [Documentation]    Check that a requirement does not have duplicate suite filenames in the trace output JSON file.
    [Tags]      Trace
    ${json}   ${req_keys}=    Load Requirement Keys

    ${req} =  Get From Dictionary    ${json}[report][${req_keys}[0]]    suite

    ${num_suites}=  Get Length    ${req}
    Log To Console    Checking requirement: ${req}
    Log To Console    Number of suites for requirement ${req_keys}[0]: ${num_suites}
    ${unique_list}=  Remove Duplicates  ${req}
    ${num_unique_suites}=  Get Length    ${unique_list}

    Should Be Equal As Integers    ${num_suites}    ${num_unique_suites}

*** Keywords ***
Sync Database
    Log To Console    Syncing database with requirements from ${REQ_YAML}
    Log To Console    Current Directory: ${CURDIR}
    Run CLI Command   sync from-yaml --file ${REQ_YAML}

Run Robot And Trace
    Save State
    Sync Database
    Run Process         robot    --outputdir    ${CURDIR}    ${ROBOT_TESTS}
    File Should Exist   ${OUTPUT_XML}
    Run CLI Command     trace --robot-output=${OUTPUT_XML} --output=${TRACE_JSON} --fmt json

Status Should be Valid
    [Arguments]    ${status}
    ${allowed}      Create List     NOT TESTED    FAILED    PASSED
    Run Keyword If    '${status}' not in ${allowed}    Fail    Invalid status: ${status}. Allowed statuses are: ${allowed}

Load Requirement Keys
    ${json}=    Load JSON From File    ${OUTPUT_TRACE}
    Should Have Value In Json    ${json}    report
    ${req_keys}=  Get Dictionary Keys    ${json}[report]  sort_keys=False
    RETURN      ${json}     ${req_keys}

*** Keywords ***
Remove Test Files
    Remove Reports Folder
    # Remove File    ${OUTPUT_TRACE}
    # Remove File    ${OUTPUT_XML}


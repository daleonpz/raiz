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

Check All Requirements Are Present
    [Documentation]    Check that all requirements are present and valid in the trace output JSON file.
    [Tags]      Trace
    ${json}   ${req_keys}=    Load Requirement Keys

    Log To Console    Total requirements found: ${req_keys}

    FOR     ${req_key}  IN  @{req_keys}
        Log To Console    Requirement ID: ${req_key}
        Dictionary Should Contain Key    ${json}[report][${req_key}]    linked_tests
        Dictionary Should Contain Key    ${json}[report][${req_key}]    test_results

        ${test_results}=  Get From Dictionary    ${json}[report][${req_key}]    test_results

        FOR     ${tests}    IN  @{test_results}
            Status Should be Valid    ${tests[2]}
        END
    END

Check Untested Requirement is REQ-005
    [Documentation]    Check that the untested requirement is REQ-005.
    [Tags]      Trace
    ${json}   ${req_keys}=    Load Requirement Keys
    ${untested_req_key}=  Set Variable    None

    ${linked_tests}=  Get From Dictionary    ${json}[report][REQ-005]    linked_tests
    ${test_results}=  Get From Dictionary    ${json}[report][REQ-005]    test_results
    Should Be Empty    ${linked_tests}
    Should Be Empty    ${test_results}

Check Non-existent REQ-999 Is Not Included
    [Documentation]    Check that the non-existent requirement REQ-999 is not included in the trace output JSON file.
    [Tags]      Trace
    ${json}   ${req_keys}=    Load Requirement Keys

    FOR   ${req_id}  IN  @{req_keys}
        Log To Console    Checking requirement ID: ${req_id}
        Should Not Be Equal    ${req_id}    REQ-999
    END

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
    ${allowed}      Create List     NOT TESTED    FAIL    PASS
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


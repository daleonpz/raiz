*** Settings ***
Suite Setup       Save State
Suite Teardown    Remove Reports Folder
Resource          resources/cli_keywords.robot
Library           OperatingSystem

*** Variables ***
${CMD}            python3 req.py

*** Test Cases ***

Remove Nonexistent Requirement Should Fail
    [Documentation]    Removing a non-existent requirement ID (e.g. 9999) must exit with a non-zero code.
    [Tags]    Remove    EdgeCase
    ${result}=    Run Process    ${CMD} rm 9999    shell=True
    Should Not Be Equal As Integers    ${result.rc}    0

Remove Requirement With ID Zero Should Fail
    [Documentation]    Requirement IDs start at 1; removing ID 0 must be rejected.
    [Tags]    Remove    EdgeCase
    ${result}=    Run Process    ${CMD} rm 0    shell=True
    Should Not Be Equal As Integers    ${result.rc}    0

Remove Requirement With Negative ID Should Fail
    [Documentation]    Negative IDs are not valid requirement IDs and must be rejected.
    [Tags]    Remove    EdgeCase
    ${result}=    Run Process    ${CMD} rm -- -5    shell=True
    Should Not Be Equal As Integers    ${result.rc}    0

Update Nonexistent Requirement Should Fail
    [Documentation]    Updating a requirement that does not exist must exit with a non-zero code.
    [Tags]    Update    EdgeCase
    ${result}=    Run Process    ${CMD} update 9999 --field type --value constraint    shell=True
    Should Not Be Equal As Integers    ${result.rc}    0

Show Requirements With Combined Type And Domain Filter
    [Documentation]    Filtering by both --type and --domain must use AND logic and return only
    ...                requirements that match both criteria. Previously this produced invalid SQL.
    [Tags]    Show    EdgeCase
    Add Requirement    BLE functional req    functional    ble
    Add Requirement    Network functional req    functional    network
    Add Requirement    Network non-functional req    non-functional    network
    ${out}=       Run CLI Command    show all --json --type functional --domain network
    ${filtered}=  Convert String To JSON    ${out}
    Length Should Be    ${filtered}    1
    Should Be Equal As Strings    ${filtered[0]["type"]}      functional
    Should Be Equal As Strings    ${filtered[0]["domain"]}    network

Sync From Nonexistent YAML Should Fail
    [Documentation]    Syncing from a YAML file that does not exist must fail with a non-zero exit code.
    [Tags]    Sync    EdgeCase
    ${result}=    Run Process    ${CMD} sync from-yaml --file /nonexistent/path/file.yaml    shell=True
    Should Not Be Equal As Integers    ${result.rc}    0

Sync From YAML With Missing Fields Should Fail
    [Documentation]    Syncing from a YAML file where a requirement is missing the uuid field must fail.
    [Tags]    Sync    EdgeCase
    ${content}=    Set Variable    - description: Missing uuid field\n  type: functional\n  domain: ble\n
    Create File    /tmp/invalid_reqs.yaml    ${content}
    ${result}=    Run Process    ${CMD} sync from-yaml --file /tmp/invalid_reqs.yaml    shell=True
    Should Not Be Equal As Integers    ${result.rc}    0
    [Teardown]    Remove File    /tmp/invalid_reqs.yaml

Sync From Empty YAML Should Fail
    [Documentation]    Syncing from an empty YAML file must fail gracefully without corrupting the DB.
    [Tags]    Sync    EdgeCase
    Create File    /tmp/empty_reqs.yaml    ${EMPTY}
    ${reqs_before}=    List Requirements As JSON
    ${result}=         Run Process    ${CMD} sync from-yaml --file /tmp/empty_reqs.yaml    shell=True
    Should Not Be Equal As Integers    ${result.rc}    0
    ${reqs_after}=     List Requirements As JSON
    Length Should Be    ${reqs_after}    ${reqs_before.__len__()}
    [Teardown]    Remove File    /tmp/empty_reqs.yaml

Remove Requirement Leaves No Gaps In IDs
    [Documentation]    After removing a requirement from the middle, the remaining IDs must be
    ...                contiguous starting from REQ-001.
    [Tags]    Remove    EdgeCase
    Add Requirement    Gap test req A    functional    ble
    Add Requirement    Gap test req B    functional    ble
    Add Requirement    Gap test req C    functional    ble
    ${reqs}=      List Requirements As JSON
    ${count}=     Get Length    ${reqs}
    Remove Requirement    1
    ${reqs}=    List Requirements As JSON
    ${new_count}=    Get Length    ${reqs}
    Should Be Equal As Integers    ${new_count}    ${count - 1}
    Should Be Equal As Strings    ${reqs[0]["id"]}    REQ-001
    Should Be Equal As Strings    ${reqs[-1]["id"]}    REQ-00${new_count}

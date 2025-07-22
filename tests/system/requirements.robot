*** Settings ***
Suite Setup       Save State
Suite Teardown    Remove Reports Folder
Resource          resources/cli_keywords.robot

*** Test Cases ***

Add Requirement Should Work
    [Documentation]   This test case verifies that adding a requirement works correctly.
    [Tags]  Add
    Add Requirement    First test requirement    functional    ble
    ${reqs}=           List Requirements As JSON
    Should Be Equal As Strings    ${reqs[-1]["description"]}    First test requirement

Add Multiple Requirements And Verify Order
    [Documentation]   This test case verifies that adding multiple requirements works correctly and they are in the right order.
    [Tags]  Add
    Add Requirement    Second one    functional    ble
    Add Requirement    Third one    constraint    logging
    ${reqs}=           List Requirements As JSON
    Length Should Be    ${reqs}    3
    Should Be Equal As Strings    ${reqs[1]["id"]}    REQ-002
    Should Be Equal As Strings    ${reqs[2]["type"]}    constraint

Update Requirement Domain Should Change Only Domain
    [Documentation]   This test case verifies that updating a requirement's domain changes only the domain.
    [Tags]  Update
    Update Requirement    2    domain   new_domain 
    ${reqs}=              List Requirements As JSON
    Should Be Equal As Strings    ${reqs[1]["domain"]}   new_domain
    Should Be Equal As Strings    ${reqs[1]["type"]}   functional

Update Requirement Type Should Change Only Type
    [Documentation]   This test case verifies that updating a requirement's type changes only the type.
    [Tags]  Update
    Update Requirement    2    type    constraint 
    ${reqs}=              List Requirements As JSON
    Should Be Equal As Strings    ${reqs[1]["domain"]}   new_domain
    Should Be Equal As Strings    ${reqs[1]["type"]}    constraint

Remove Requirement Should Renumber
    [Documentation]   This test case verifies that removing a requirement renumbers the remaining requirements.
    [Tags]  Remove
    ${reqs}=              List Requirements As JSON
    Length Should Be      ${reqs}    3
    Remove Requirement    2
    ${reqs}=              List Requirements As JSON
    Length Should Be      ${reqs}    2
    Should Be Equal As Strings    ${reqs[0]["id"]}    REQ-001
    Should Be Equal As Strings    ${reqs[1]["id"]}    REQ-002

Export To YAML Should Match DB State
    [Documentation]   This test case verifies that exporting requirements to YAML matches the current state in the database.
    [Tags]  Sync
    ${reqs1}=           List Requirements As JSON
    Sync To YAML
    ${file}=            Get File    .requirements_test.yaml
    Should Contain      ${file}    ${reqs1[0]["description"]}
    Should Contain      ${file}    ${reqs1[1]["description"]}

Import From YAML Should Restore Requirements
    [Documentation]   This test case verifies that importing requirements from YAML restores the requirements correctly.
    [Tags]  Sync
    Remove Requirement    1
    ${reqs2}=             List Requirements As JSON
    Length Should Be      ${reqs2}    1

    Sync From YAML
    ${reqs3}=             List Requirements As JSON
    Length Should Be      ${reqs3}    2
    Should Contain        ${reqs3[0]["description"]}    First test requirement


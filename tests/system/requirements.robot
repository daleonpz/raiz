*** Settings ***
Suite Setup       Save State
Suite Teardown    Remove Reports Folder
Resource          resources/cli_keywords.robot

*** Test Cases ***

Add Requirement Should Work
    [Tags]  Add
    Add Requirement    First test requirement    functional    ble
    ${reqs}=           List Requirements As JSON
    Should Be Equal As Strings    ${reqs[-1]["description"]}    First test requirement

Add Multiple Requirements And Verify Order
    [Tags]  Add
    Add Requirement    Second one    functional    ble
    Add Requirement    Third one    constraint    logging
    ${reqs}=           List Requirements As JSON
    Length Should Be    ${reqs}    3
    Should Be Equal As Strings    ${reqs[1]["id"]}    REQ-002
    Should Be Equal As Strings    ${reqs[2]["type"]}    constraint

Update Requirement Domain Should Change Only Domain
    [Tags]  Update
    Update Requirement    2    domain   new_domain 
    ${reqs}=              List Requirements As JSON
    Should Be Equal As Strings    ${reqs[1]["domain"]}   new_domain
    Should Be Equal As Strings    ${reqs[1]["type"]}   functional

Update Requirement Type Should Change Only Type
    [Tags]  Update
    Update Requirement    2    type    constraint 
    ${reqs}=              List Requirements As JSON
    Should Be Equal As Strings    ${reqs[1]["domain"]}   new_domain
    Should Be Equal As Strings    ${reqs[1]["type"]}    constraint

Remove Requirement Should Renumber
    [Tags]  Remove
    ${reqs}=              List Requirements As JSON
    Length Should Be      ${reqs}    3
    Remove Requirement    2
    ${reqs}=              List Requirements As JSON
    Length Should Be      ${reqs}    2
    Should Be Equal As Strings    ${reqs[0]["id"]}    REQ-001
    Should Be Equal As Strings    ${reqs[1]["id"]}    REQ-002

Export To YAML Should Match DB State
    [Tags]  Sync
    ${reqs1}=           List Requirements As JSON
    Sync To YAML
    ${file}=            Get File    .requirements_test.yaml
    Should Contain      ${file}    ${reqs1[0]["description"]}
    Should Contain      ${file}    ${reqs1[1]["description"]}

Import From YAML Should Restore Requirements
    [Tags]  Sync
    Remove Requirement    1
    ${reqs2}=             List Requirements As JSON
    Length Should Be      ${reqs2}    1

    Sync From YAML
    ${reqs3}=             List Requirements As JSON
    Length Should Be      ${reqs3}    2
    Should Contain        ${reqs3[0]["description"]}    First test requirement

*** Keywords ***
Remove Reports Folder
    Remove File         .requirements_test.yaml
    Remove File         .req_cache/requirements.db
    Move File           .req_cache/requirements.db.orig    .req_cache/requirements.db

Save State
    Move File           .req_cache/requirements.db     .req_cache/requirements.db.orig

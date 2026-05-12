*** Settings ***
Library           OperatingSystem
Library           Process
Library           Collections
Library           JSONLibrary

*** Variables ***
${CMD}            raiz

*** Keywords ***
Run CLI Command
    [Arguments]    ${args}
    ${result}=     Run Process    ${CMD} ${args}    shell=True
    Should Be Equal As Integers    ${result.rc}    0
    RETURN       ${result.stdout}

Add Requirement
    [Arguments]    ${desc}    ${type}    ${domain}
    ${input}=      Catenate    SEPARATOR=\n    ${desc}    ${type}    ${domain}
    Run Process    ${CMD} add    stdin=${input}    shell=True

Remove Requirement
    [Arguments]    ${id}
    Run CLI Command    rm ${id}

Update Requirement
    [Arguments]    ${id}    ${field}    ${value}
    Run CLI Command    update ${id} ${field} ${value}

List Requirements As JSON
    ${out}=        Run CLI Command    show all --json
    ${parsed}=     Convert String To JSON    ${out}
    RETURN       ${parsed}

Sync From YAML
    Run CLI Command    import --format yaml --file .requirements_test.yaml

Sync To YAML
    Run CLI Command    export --format yaml --file .requirements_test.yaml

Save State
    ${exists}=    Run Keyword And Return Status
    ...    File Should Exist    .req_cache/requirements.db
    IF    ${exists}
        Move File    .req_cache/requirements.db    .req_cache/requirements.db.orig
    END

Remove Reports Folder
    Remove File    .requirements_test.yaml
    Remove File    .req_cache/requirements.db

    ${backup_exists}=    Run Keyword And Return Status
    ...    File Should Exist    .req_cache/requirements.db.orig
    IF    ${backup_exists}
        Move File    .req_cache/requirements.db.orig    .req_cache/requirements.db
    END

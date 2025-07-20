*** Settings ***
Library           OperatingSystem
Library           Process
Library           Collections
Library           JSONLibrary

*** Variables ***
${CMD}            python3 req.py

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
    ${out}=        Run CLI Command    list all --json
    ${parsed}=     Convert String To JSON    ${out}
    RETURN       ${parsed}

Sync From YAML
    Run CLI Command    sync from-yaml --file .requirements_test.yaml

Sync To YAML
    Run CLI Command    sync to-yaml --file .requirements_test.yaml

*** Settings ***

Documentation  Health - Regulatory Inspector permissions

Library                 Selenium2Library  timeout=10  implicit_wait=0
#Library                 bika.lims.tests.base.Keywords
Library                 Collections
Resource                bika/lims/tests/keywords.txt
Variables               plone/app/testing/interfaces.py
Suite Setup             Start browser
#Suite Teardown          Close All Browsers


*** Test Cases ***

Patients View Access

    Log in      test_regulatoryinspector  test_regulatoryinspector
    Go to       http://localhost:55001/plone/patients
    Wait Until Page Contains    John Grisham
    Wait Until Page Contains    Pam Morrison


Cases View Access

    Log in  test_labmanager  test_labmanager
    Create Case
    Log out

    # Check regulatory inspector
    Log in      test_regulatoryinspector  test_regulatoryinspector
    Go to       http://localhost:55001/plone/batches/B-001


*** Keywords ***

Start Browser
    Open browser        http://localhost:55001/plone/
    Set selenium speed  0


Select from datepicker
    [Documentation]    this doesn't do any tricks yet, just clicks the link.
    [Arguments]        ${locator}
    ...                ${number}
    Click Element      ${locator}
    Click link         ${number}


SelectSpecificFromDropdown
    [Arguments]  ${Element}=
    ...          ${Option}=
    Input Text  ${Element}  ${Option}
    sleep  0.5
    #select the first item in the dropdown and return status
    ${STATUS}  Run Keyword And Return Status  Click Element  xpath=//div[contains(@class,'cg-DivItem')]
    #if error or no content in dropdown output warning and continue
    Run Keyword If  '${STATUS}' == 'False'  Log  Error in attemting to select first specific item in dropdown - could also be empty: ${Element}  WARN


Create Case
    [Documentation]     Add one case for patient John Grisham
    Go to  http://localhost:55001/plone/batches
    Wait Until Page Contains    Add
    Click Link                  Add
    Wait Until Page Contains Element  Patient_uid
    Select From Dropdown  Patient       John Grisham
    Select From Dropdown  Doctor       Andrew
    Click Button                Save
    Wait Until Page Contains    Changes saved.


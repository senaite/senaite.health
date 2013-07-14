*** Settings ***

Documentation  Health - Regulatory Inspector permissions

Library                 Selenium2Library  timeout=10  implicit_wait=0
#Library                 bika.lims.tests.base.Keywords
Library                 Collections
#Resource                keywords.txt
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
    
    Create Case
    
    # Check regulatory inspector
    Log in      test_regulatoryinspector  test_regulatoryinspector
    Go to       http://localhost:55001/plone/batches
    Wait Until Page Contains    John Grisham
    Wait Until Page Contains    Pam Morrison    




*** Keywords ***

Start Browser
    Open browser        http://localhost:55001/plone/
    Set selenium speed  0
    
Log in
    [Arguments]  ${userid}  ${password}
    
    Go to       http://localhost:55001/plone/login_form
    Page should contain element  __ac_name
    Page should contain element  __ac_password
    Page should contain button  Log in
    Input text  __ac_name  ${userid}
    Input text  __ac_password  ${password}
    Click Button  Log in

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
    Log in  test_labmanager  test_labmanager
    Go to  http://localhost:55001/plone/batches
    Wait Until Page Contains    Add
    Click Link                  Add
    Wait Until Page Contains Element  Patient_uid
    Select Specific From Dropdown  Patient       John Grisham
    Click Button                Save
    Wait Until Page Contains    Changes saved.
    
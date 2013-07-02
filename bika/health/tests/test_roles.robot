*** Settings ***

Documentation  Health - User roles permissions

Library                 Selenium2Library  timeout=10  implicit_wait=0
#Library                 bika.lims.tests.base.Keywords
Library                 Collections
#Resource                keywords.txt
Variables               plone/app/testing/interfaces.py
Suite Setup             Start browser
#Suite Teardown         Close All Browsers

*** Test Cases ***

Regulatory Inspector
    Log in              test_regulatoryinspector  test_regulatoryinspector
    
    # Check if regulatory inspector has access to patients view
    Go to  http://localhost:55001/plone/patients
    Wait Until Page Contains    Active


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

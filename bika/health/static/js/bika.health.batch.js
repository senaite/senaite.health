/**
 * Controller class for Batch edit/creation view
 */
function HealthBatchEditView() {

    var that = this;

    // ------------------------------------------------------------------------
    // PUBLIC ACCESSORS
    // ------------------------------------------------------------------------

    /**
     * The current PatientUID.
     * Returns the stored value in the form. If none, return null
     */
    this.getPatientUID = function() {
        return getElementAttr('#Patient', 'uid');
    }

    /**
     * The current ClientUID.
     * Returns the stored value in the form. If none, return null
     */
    this.getClientUID = function() {
        return getElementAttr('#Client', 'uid');
    }

    /**
     * The Birth Date of the current Patient
     */
    this.getPatientBirthDate = function() {
        return $('input[name="PatientBirthDate"]').val();
    }

    /**
     * The gender of the current Patient
     */
    this.getPatientGender = function() {
        return $('input[name="PatientGender"]').val().toLowerCase();
    }

    // ------------------------------------------------------------------------
    // PUBLIC FUNCTIONS
    // ------------------------------------------------------------------------

    /**
     * Entry-point method for BatchEditView
     */
    this.load = function() {
        // Add missing fields
        if (!$('input[name="PatientBirthDate"]').length) {
            $("body").append('<input type="hidden" name="PatientBirthDate"/>');
        }
        if (!$('input[name="PatientGender"]').length){
            $("body").append('<input type="hidden" name="PatientGender"/>');
        }

        // If Patient selected, fill additional fields (BirthDate, etc.)
        var patient_uid = that.getPatientUID();
        if (patient_uid != null) {
            that.fillPatient(patient_uid);
        }

        // If Client selected, apply search filters
        var client_uid = that.getClientUID();
        if (client_uid != null) {
            that.fillClient(client_uid);
        }

        // Load Event Handlers
        loadEventHandlers();

        fillPatientAgeAtCaseOnsetDate();
        toggleMenstrualStatus();
        toggleSymptoms();

        // Advertisement for too hight/low Basal body temperature
        basalBodyTemperatureControl();
    }

    /**
     * Apply filters for patients listing reference widget and doctors when
     * client changes
     */
    this.fillClient = function(uid) {
        applyFilter($("#Patient"), 'getPrimaryReferrerUID', uid);
        applyFilter($("#ClientPatientID"), 'getPrimaryReferrerUID', uid);
        applyFilter($("#Doctor"), 'getPrimaryReferrerUID', [uid, null]);
    }

    /**
     * Searches a patient using the Patient UID. If found, fill the form with the
     * data retrieved from that Patient (Client, ClientPatientID, Gender, etc.).
     * If no patient found, reset to default all Patient-related fields
     * @param uid the Patient UID
     * @return true if the patient was found and input fields have been filled
     */
    this.fillPatient = function(uid) {
        var succeed = false;
        if (uid != '' && uid != null) {
            $.ajax({
                url: window.portal_url + "/getpatientinfo",
                type: 'POST',
                async: false,
                data: {
                  '_authenticator': $('input[name="_authenticator"]').val(),
                  'PatientUID': uid
                },
                dataType: "json",
                success: function(data, textStatus, $XHR){
                    if (data['PatientUID'] != '') {
                        // Set Client info
                        $('#Client').val(data['ClientTitle']);
                        $('#Client').attr('uid', data['ClientUID']);
                        $('#Client_uid').val(data['ClientUID']);

                        // Set Patient info
                        $('#Patient').val(data['PatientFullname']);
                        $('#Patient').attr('uid', data['PatientUID']);
                        $('#Patient_uid').val(data['PatientUID']);

                        // Set CPID Info
                        $('#ClientPatientID').val(data['ClientPatientID']);
                        $('#ClientPatientID').attr('uid', data['PatientUID']);
                        $('#ClientPatientID_uid').attr('uid', data['PatientUID']);

                        // Set Patient's additional info
                        $('input[name="PatientBirthDate"]').val(data['PatientBirthDate']);
                        $('input[name="PatientGender"]').val(data['PatientGender']);

                        // Set Patient's menstrual status if female
                        if (data['PatientGender'] == 'female'
                            && data['PatientMenstrualStatus'] != null
                            && data['PatientMenstrualStatus'].length > 0) {
                            ms = data['PatientMenstrualStatus'][0];

                            // Set hysterectomy fields
                            $("#MenstrualStatus-Hysterectomy-0").attr('checked', ms['Hysterectomy']);
                            $("#MenstrualStatus-HysterectomyYear-0").val(ms['HysterectomyYear']);
                            if (!ms['Hysterectomy']) {
                                $("#MenstrualStatus-HysterectomyYear-0").val('');
                                $("#MenstrualStatus-HysterectomyYear-0").parent().hide();
                            } else {
                                $("#MenstrualStatus-HysterectomyYear-0").parent().show();
                                $("#MenstrualStatus-HysterectomyYear-0").focus()
                            }

                            // Set ovaries removed fields
                            $("#MenstrualStatus-OvariesRemoved-0").attr('checked', ms['OvariesRemoved']);
                            $("#MenstrualStatus-OvariesRemovedNum-0[value=1]").attr('checked',ms['OvariesRemovedNum']==1);
                            $("#MenstrualStatus-OvariesRemovedNum-0[value=2]").attr('checked',ms['OvariesRemovedNum']==2);
                            $("#MenstrualStatus-OvariesRemovedYear-0").val(ms['OvariesRemovedYear']);
                            if (!ms['OvariesRemoved']) {
                                $("#MenstrualStatus-OvariesRemovedNum-0:radio").attr('checked', false);
                                $("#MenstrualStatus-OvariesRemovedYear-0").val('');
                                $("#MenstrualStatus-OvariesRemovedYear-0").parent().hide();
                            } else {
                                $("#MenstrualStatus-OvariesRemovedYear-0").parent().show();
                            }
                        }
                    }
                }
            });
            succeed = ($("#Patient").attr('uid') == uid);
        }
        if (!succeed) {
            // Reset patient fields
            $('#Patient').val('');
            $('#Patient').attr('uid', '');
            $('#Patient_uid').val('');
            $('#ClientPatientID').val('');
            $('#ClientPatientID').attr('uid', '');
            $('#ClientPatientID_uid').attr('uid', '');
            $('input[name="PatientBirthDate"]').val('');
            $('input[name="PatientGender"]').val('');
        }
        fillPatientAgeAtCaseOnsetDate();
        toggleMenstrualStatus();
        toggleSymptoms();
        return succeed;
    }

    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------

    /**
     * Management of events and triggers
     */
    function loadEventHandlers() {
        $("#Client").bind("selected paste blur", function(){
            var uid = $(this).attr('uid');
            that.fillClient(uid);
            // Reset patient fields
            that.fillPatient(null);
        });

        $("#Patient").bind("selected paste blur", function(){
            var puid = $(this).attr('uid');
            that.fillPatient(puid);
        });

        $("#ClientPatientID").bind("selected paste blur", function() {
            var puid = $(this).attr('uid');
            that.fillPatient(puid);
        });

        $("#OnsetDate").live('change', function() {
            fillPatientAgeAtCaseOnsetDate();
        });
    }

    /**
     * Retrieves the value of the specified attribute from the
     * defined element. If no value or empty, returns null
     * @param element from which to retrieve the value of the attribute
     * @returns the value of the attribute or null
     */
    function getElementAttr(element, attribute) {
        val = $(element).attr(attribute);
        return (val != null && $.trim(val) != '') ? $.trim(val) : null;
    }

    function applyFilter(combo, filterkey, filtervalue) {
        base_query=$.parseJSON($(combo).attr("base_query"));
        if (base_query != null) {
            base_query[filterkey] = filtervalue;
            options = $.parseJSON($(combo).attr("combogrid_options"));
            options['force_all']='false';
            $(combo).attr("base_query", $.toJSON(base_query));
            $(combo).attr("combogrid_options", $.toJSON(options));
            referencewidget_lookups($(combo));
        }
    }

    /**
     * Shows/Hide the symptoms according to the current Patient Gender.
     * If no patient gender found, shows only the symptoms for gender 'dk'
     */
    function toggleSymptoms() {
        if ($("#Symptoms_table").length) {
            // Show/Hide the symptoms according to Patient's gender
            gender = that.getPatientGender();
            $("#Symptoms_table tr.symptom-item").find('td').hide();
            $("#Symptoms_table tr.symptom-item.gender-"+gender).find('td').show();
            $("#Symptoms_table tr.symptom-item.gender-dk").find('td').show();
        }
    }

    /**
     * Shows the menstrual status if the current gender is 'female'. Otherwise,
     * hide the menstrual status section.
     */
    function toggleMenstrualStatus() {
        if ($('#archetypes-fieldname-MenstrualStatus').length){
            // Show/Hide MenstrualStatus widget depending on patient's gender
            gender = that.getPatientGender();
            if (gender=='female') {
                $('#archetypes-fieldname-MenstrualStatus').show();
            } else {
                $("#MenstrualStatus-FirstDayOfLastMenses-0").val('');
                $("#MenstrualCycleType-0").val('');
                $("#MenstrualStatus-Pregnant-0").attr('checked', false);
                $("#MenstrualStatus-MonthOfPregnancy-0").val('');
                $("#MenstrualStatus-Hysterectomy-0").attr('checked', false);
                $("#MenstrualStatus-HysterectomyYear-0").val('');
                $("#MenstrualStatus-OvariesRemoved-0").attr('checked', false);
                $("#MenstrualStatus-OvariesRemovedNum-0:radio").attr('checked', false);
                $("#MenstrualStatus-OvariesRemovedYear-0").val('');
                $('#archetypes-fieldname-MenstrualStatus').hide();
            }
        }
    }

    /**
     * Sets the value for the 'Patient Age At Case Onset Date'.
     * If no Patient selected or if it has no BirthDate, sets empty value.
     */
    function fillPatientAgeAtCaseOnsetDate() {
        var now = new Date($("#OnsetDate").val());
        var dob = new Date(that.getPatientBirthDate());
        var ageday = ""
        var agemonth = ""
        var ageyear = ""
        if (now!= undefined && now != null && dob!=undefined && dob != null && now >= dob){
            var currentday=now.getDate();
            var currentmonth=now.getMonth()+1;
            var currentyear=now.getFullYear();
            var birthday=dob.getDate();
            var birthmonth=dob.getMonth()+1;
            var birthyear=dob.getFullYear();
            ageday = currentday-birthday;
            agemonth=0;
            ageyear=0;

            if (ageday < 0) {
                currentmonth--;
                if (currentmonth < 1) {
                    currentyear--;
                    currentmonth = currentmonth + 12;
                }
                dayspermonth = 30;
                if (currentmonth==1 || currentmonth==3 ||
                    currentmonth==5 || currentmonth==7 ||
                    currentmonth==8 || currentmonth==10||
                    currentmonth==12) {
                    dayspermonth = 31;
                } else if (currentmonth == 2) {
                    dayspermonth = 28;
                    if(!(currentyear%4) && (currentyear%100 || !(currentyear%400))) {
                        dayspermonth++;
                    }
                }
                ageday = ageday + dayspermonth;
            }

            agemonth = currentmonth - birthmonth;
            if (agemonth < 0) {
                currentyear--;
                agemonth = agemonth + 12;
            }
            ageyear = currentyear - birthyear;

            $("#OnsetDate").next().remove(".warning");
        }
        else if (now < dob) {
            $("#PatientAgeAtCaseOnsetDate_day").next().remove(".warning");
            $("#OnsetDate").parent().append("<span class = 'warning'><img title='Onset Date must be bigger than Patients Birth Date' src='http://localhost:8080/Plone/++resource++bika.lims.images/warning.png'></span>");
        }
        $("#PatientAgeAtCaseOnsetDate_year").val(ageyear);
        $("#PatientAgeAtCaseOnsetDate_month").val(agemonth);
        $("#PatientAgeAtCaseOnsetDate_day").val(ageday);
    }

    function basalBodyTemperatureControl() {
    $( "[id^='BasalBodyTemperature-Day']" ).change(function() {
        if ( parseInt($(this).val()) > 41 ) {
        $(this).next().remove(".warning");
        $(this).parent().append("<span class = 'warning'><img title='Very high temperature' src='http://localhost:8080/Plone/++resource++bika.lims.images/warning.png'></span>");
        }
        else if ( parseInt($(this).val()) < 32 ) {
        $(this).next().remove(".warning");
        $(this).parent().append("<span class = 'warning'><img title='Very low temperature' src='http://localhost:8080/Plone/++resource++bika.lims.images/warning.png'></span>");
        }
        else {
        $(this).next().remove(".warning");
        }
    });
    }
}

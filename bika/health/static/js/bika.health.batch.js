/**
 * Controller class for Batch readonly view
 */
function HealthBatchViewView() {

    /**
     * Entry-point method for BatchViewView
     */
    this.load = function() {

        // These look silly in the edit screen under "Additional Notes"
        $('div[id^="archetypes-fieldname-Remarks-"]').remove();
    }
}

/**
 * Controller class for Batch edit/creation view
 */
function HealthBatchEditView() {

    var that = this;
    var refpatientuid = null;
    var refclientuid = null;

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
     * The current DoctorUID.
     * Returns the stored value in the form. If none, returns null
     */
    this.getDoctorUID = function() {
        return getElementAttr('#Doctor', 'uid');
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

    /**
     * Returns the referrer PatientUID if the current view referrer is a
     * Patient's batches view. Otherwise, returns null.
     * returns the Patient UID. Otherwise, returns null
     * @return patientuid or null
     */
    this.getPatientUIDReferrer = function() {
        if (refpatientuid == null) {
            // Getting the cookie with the patient's uid
            // -- readCookie is giving me ""uid""
            var cookie = readCookie('patient_uid');
            var cpuid;
            if (cookie != null){
                cpuid = cookie.replace(/"/g,'')
            };
            // Without cpuid look for the referrer page url
            if (!cpuid && document.referrer.search('/patients/') >= 0) {
                pid = document.referrer.split("patients")[1].split("/")[1];
                $.ajax({
                    url: window.portal_url + "/getpatientinfo",
                    type: 'POST',
                    async: false,
                    data: {'_authenticator': $('input[name="_authenticator"]').val(),
                           'PatientID': pid,},
                    dataType: "json",
                    success: function(data, textStatus, $XHR) {
                        if (data['PatientUID'] != null && data['PatientUID']!='') {
                            refpatientuid = data['PatientUID'] != '' ? data['PatientUID'] : null;
                            refclientuid = data['ClientUID'] != '' ? data['ClientUID'] : null;
                        }
                    }
                });
            } else {
                // Delete cookie
                document.cookie = "patient_uid=; expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;";
                refpatientuid = cpuid;
            }
        }
        return refpatientuid != '' ? refpatientuid : null;
    }

    /**
     * Returns the referrer ClientUID if the current view referrer is a Client
     * batches view or. If the current view referrer is a Patient's batch view,
     * returns the Client UID from that patient. Otherwise, returns null
     * @return clientuid or null
     */
    this.getClientUIDReferrer = function() {
        // Force first to check if the referrer is a Patient Batches view. In
        // that case, the refclientuid var will be set by the following method
        this.getPatientUIDReferrer();
        if (refclientuid == null && document.referrer.search('/clients/') >= 0) {
            clientid = document.referrer.split("clients")[1].split("/")[1];
            $.ajax({
                url: window.portal_url + "/clients/" + clientid + "/getClientInfo",
                type: 'POST',
                async: false,
                data: {'_authenticator': $('input[name="_authenticator"]').val()},
                dataType: "json",
                success: function(data, textStatus, $XHR){
                    if (data['ClientUID'] != '') {
                        refclientuid = data['ClientUID'] != '' ? data['ClientUID'] : null;
                    }
                }
            });
        }
        // Maybe the current user is a client contact. In that case, only the
        // client the current user belongs to must be available
        if (refclientuid == null) {
            $.ajax({
                url: window.portal_url + "/ajax-client-from-current-user",
                type: 'POST',
                async: false,
                data: {'_authenticator': $('input[name="_authenticator"]').val()},
                dataType: "json",
                success: function(data, textStatus, $XHR){
                    if (data['ClientUID'] != '') {
                        refclientuid = data['ClientUID'] != '' ? data['ClientUID'] : null;
                    }
                }
            });
        }
        return refclientuid != '' ? refclientuid : null;
    }

    // ------------------------------------------------------------------------
    // PUBLIC FUNCTIONS
    // ------------------------------------------------------------------------

    /**
     * Entry-point method for BatchEditView
     */
    this.load = function() {

        // These look silly in the edit screen under "Additional Notes"
        $("#archetypes-fieldname-Remarks").remove();

        // Add missing fields
        if (!$('input[name="PatientBirthDate"]').length) {
            $("body").append('<input type="hidden" name="PatientBirthDate"/>');
        }
        if (!$('input[name="PatientGender"]').length){
            $("body").append('<input type="hidden" name="PatientGender"/>');
        }

        // Hide the client field in order to avoid cross-conflicts with Patient
        // selection.
        $('#Client').hide();
        $('#archetypes-fieldname-Client .formQuestion span[class="required"]').hide();
        $('#Client').after("<span id='Client_label'>" + $("#Client").val() + "</span>&nbsp;&nbsp;");

        rpuid = that.getPatientUIDReferrer();
        rcuid = that.getClientUIDReferrer();

        if (rpuid != null) {
            // The form comes from a Patient view. Set the default patient and
            // disable the patient, CPID and client combos.
            that.fillPatient(rpuid);
            $('#Patient').hide();
            $('#Client').hide();
            $('#ClientPatientID').hide();
            $('a.add_patient').hide();
            // $('a.edit_patient').hide();
            $('#Patient').after("<span id='Patient_label'>" + $("#Patient").val() + "</span>&nbsp;&nbsp;");
           //$('#Client').after("<span id='Client_label'>" + $("#Client").val() + "</span>");
            $('#ClientPatientID').after("<span id='ClientPatientID_label'>" + $("#ClientPatientID").val() + "</span>");
            $('#Patient_addbutton').hide();

        } else if (rcuid != null) {
            that.fillClient(rcuid);
        }

        if (rcuid != null) {
            // The form comes from a Client view. Set the default client,
            // disable the client combo and show only the patients from this
            // client inside patient-related combos
            applyFilter($("#Patient"), 'getPrimaryReferrerUID', rcuid);
            applyFilter($("#ClientPatientID"), 'getPrimaryReferrerUID', rcuid);
            // Also, show only the Doctors that are not from a different client
            applyFilter($("#Doctor"), 'getPrimaryReferrerUID', [rcuid, null]);
        }

        // By default, get the referrer uids from the form itself. If the form is
        // empty/new, both of them will be further retrieved from the referrers.
        refpatientuid = rpuid != null ? rpuid : that.getPatientUID();
        refclientuid = rcuid != null ? rcuid : that.getClientUID();

        // Fill the patient data for the current Patient
        puid = that.getPatientUID();
        if (rpuid == null) {
            that.fillPatient(puid);
        }

        // Fill the doctor data for the current Doctor
        that.fillDoctor(that.getDoctorUID());

        // Load Event Handlers
        loadEventHandlers();

        fillPatientAgeAtCaseOnsetDate();
        toggleMenstrualStatus();
        toggleSymptoms();

        // Advertismen for too hight/low Basal body temperature
        basalBodyTemperatureControl();
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
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                    'PatientUID': uid},
                dataType: "json",
                success: function(data, textStatus, $XHR){
                    if (data['PatientUID'] != '') {
                        // Set Client info
                        $('#Client').val(data['ClientTitle']);
                        $('#Client').attr('uid', data['ClientUID']);
                        $('#Client_uid').val(data['ClientUID']);
                        $('#Client_label').text(data['ClientTitle']);

                        // Set Patient info
                        $('#Patient').val(data['PatientFullname']);
                        $('#Patient').attr('uid', data['PatientUID']);
                        $('#Patient').attr('pid', data['PatientID']);
                        $('#Patient_uid').val(data['PatientUID']);
                        $('#Patient_label').text(data['PatientFullname']);

                        // Set CPID Info
                        $('#ClientPatientID').val(data['ClientPatientID']);
                        $('#ClientPatientID').attr('uid', data['PatientUID']);
                        $('#ClientPatientID_uid').attr('uid', data['PatientUID']);
                        $('#ClientPatientID_label').text(data['ClientPatientID']);

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
        if (!succeed && (uid != that.getPatientUIDReferrer()
                         || that.getPatientUIDReferrer() == null)) {
            this.resetPatient();

        } else if (!succeed && that.getPatientUIDReferrer() != null){
            console.log('Unable to retrieve the Referrer Patient for UID ' + that.getPatientUIDReferrer());

        } else if (succeed) {
            fillPatientAgeAtCaseOnsetDate();
            toggleMenstrualStatus();
            toggleSymptoms();
        }
        return succeed;
    }

    /**
     * Resets the patient of the form to the referrer patient. If no referrer
     * patient found, sets all the patient-related fields to blank.
     */
    this.resetPatient = function() {
        puid = that.getPatientUIDReferrer();
        if (puid != null) {
            this.fillPatient(puid);
        } else {
            // Clear all inputs
            // Set Client info
            $('#Client').val('');
            $('#Client').attr('uid', '');
            $('#Client_uid').val('');
            $('#Client_label').text('');

            // Set Patient info
            $('#Patient').val('');
            $('#Patient').attr('uid', '');
            $('#Patient').attr('pid', '');
            $('#Patient_uid').val('');
            $('#Patient_label').text('');

            // Set CPID Info
            $('#ClientPatientID').val('');
            $('#ClientPatientID').attr('uid', '');
            $('#ClientPatientID_uid').attr('uid', '');
            $('#ClientPatientID_label').text('');

            // Set Patient's additional info
            $('input[name="PatientBirthDate"]').val('');
            $('input[name="PatientGender"]').val('');

            fillPatientAgeAtCaseOnsetDate();
            toggleMenstrualStatus();
            toggleSymptoms();
        }
    }

    /**
     * Searches a doctor using the Doctor UID. If found, fill the form with the
     * data retrieved from that Doctor.
     * If no doctor found, reset to default all Doctor related fields
     * @param uid the Doctor UID
     * @return true if the doctor was found and input fields have been filled
     */
    this.fillDoctor = function(uid) {
        var succeed = false;
        if (uid != null && uid != '') {
            // Nothing to do (no additional input fields related with doctor)
        }
        duid = that.getDoctorUID();
        succeed = (duid != null && duid == uid);
        if (!succeed) {
            // Reset Doctor default values
            $('#Doctor').val('');
            $('#Doctor').attr('uid', '');
            $('#Doctor_uid').val('');
        }
        return succeed;
    }

    /**
     * Searches a client using the Client UID. If found, fill the form with the
     * data retrieved from that Client.
     * If no client found, reset to default all client related fields
     * @param uid the Client UID
     * @return true if the client was found and input fields have been filled
     */
    this.fillClient = function(uid) {
        var succeed = false;
        if (uid != null && uid != '') {
            // Nothing to do (no additional input fields related with doctor)
        }
        cuid = that.getClientUID();
        succeed = (cuid != null && cuid == uid);
        if (!succeed) {
            // Reset Client default values
            $('#Client').val('');
            $('#Client').attr('uid', '');
            $('#Client_uid').val('');
        }
        return succeed;
    }

    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------

    /**
     * Management of events and triggers
     */
    function loadEventHandlers() {
        $("#Patient").bind("selected paste blur", function(){
            puid = $(this).attr('uid');
            that.fillPatient(puid);
        });

        $("#Client").bind("selected paste blur", function(){
            cuid = $(this).attr('uid');
            that.fillClient(cuid);
        });

        $("#Doctor").bind("selected paste blur", function(){
            duid = $(this).attr('uid');
            that.fillDoctor(duid);
        });

        $("#OnsetDate").live('change', function() {
            fillPatientAgeAtCaseOnsetDate();
        });
        $("#ClientPatientID").bind("selected paste blur", function() {
            puid = $(this).attr('uid');
            that.fillPatient(puid);
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
        base_query[filterkey] = filtervalue;
        options = $.parseJSON($(combo).attr("combogrid_options"));
        options['force_all']='false';
        $(combo).attr("base_query", $.toJSON(base_query));
        $(combo).attr("combogrid_options", $.toJSON(options));
        referencewidget_lookups($(combo));
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
        if (now!= undefined && now != null && dob!=undefined && dob != null && now >= dob){
            var currentday=now.getDate();
            var currentmonth=now.getMonth()+1;
            var currentyear=now.getFullYear();
            var birthday=dob.getDate();
            var birthmonth=dob.getMonth()+1;
            var birthyear=dob.getFullYear();
            var ageday = currentday-birthday;
            var agemonth=0;
            var ageyear=0;

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

            $("#PatientAgeAtCaseOnsetDate_year").val(ageyear);
            $("#PatientAgeAtCaseOnsetDate_month").val(agemonth);
            $("#PatientAgeAtCaseOnsetDate_day").val(ageday);
            $("#OnsetDate").next().remove(".warning");
        }
        else if (now < dob) {
            erasePatientAgeatCaseOnsetDate();
            $("#PatientAgeAtCaseOnsetDate_day").next().remove(".warning");
            $("#OnsetDate").parent().append("<span class = 'warning'><img title='Onset Date must be bigger than Patients Birth Date' src='http://localhost:8080/Plone/++resource++bika.lims.images/warning.png'></span>");
        }
        else {
            erasePatientAgeatCaseOnsetDate();
        }
    }
    function erasePatientAgeatCaseOnsetDate() {
        $("#PatientAgeAtCaseOnsetDate_year").val('');
        $("#PatientAgeAtCaseOnsetDate_month").val('');
        $("#PatientAgeAtCaseOnsetDate_day").val('');
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

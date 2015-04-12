'use strict;'

/**
 * Controller class for Patient edit/creation view
 */
function HealthPatientEditView() {

    var that = this;

    // ------------------------------------------------------------------------
    // PUBLIC FUNCTIONS
    // ------------------------------------------------------------------------


    /**
     * Returns the referrer ClientUID if the current view referrer is a Client
     * patients view. If the current view referrer is a Client's patient view,
     * returns the Client UID. Otherwise, returns null
     * @return clientuid or null
     */
    this.getClientUIDReferrer = function() {
        // Force first to check if the referrer is a Patient Batches view. In
        // that case, the refclientuid var will be set by the following method
        var refclientuid = '';
        if (document.referrer.search('/clients/') >= 0) {
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
        return refclientuid != '' ? refclientuid : null;
    }

    /**
     * Entry-point method for PatientEditView
     */
    this.load = function() {

        // These are not meant to show up in the main patient base_edit form.
        // they are flagged 'visible' though, so they do show up when requested.
        $('.template-base_edit #archetypes-fieldname-Allergies').hide();
        $('.template-base_edit #archetypes-fieldname-TreatmentHistory').hide();
        $('.template-base_edit #archetypes-fieldname-ImmunizationHistory').hide();
        $('.template-base_edit #archetypes-fieldname-TravelHistory').hide();
        $('.template-base_edit #archetypes-fieldname-ChronicConditions').hide();
        // It fills out the Insurance Company field.
        var frominsurance = document.referrer.search('/bika_insurancecompanies/') >= 0;
        if (frominsurance){
            // The current Patient add View comes from an insurance companies folder view.
            // Automatically fill the Patient field
            var iid = document.referrer.split("/bika_insurancecompanies/")[1].split("/")[0];
            fillInsuranceCompanyReferrer(iid);
        }
    // Adapt datepicker to current needs
    $("#BirthDate").datepicker("destroy");
    $("#BirthDate").datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth:true,
        changeYear:true,
        yearRange: "-100:+0"
    });

        if ($('#archetypes-fieldname-Gender #Gender').val()!='female') {
            $('#archetypes-fieldname-MenstrualStatus').hide();
        }
        if ($('#patient-base-edit')) {
            loadAnonymous();
        }
        rcuid = that.getClientUIDReferrer();
        if (rcuid != null) {
            // The user comes from the Client's Patients view
            fillClient(rcuid);
        }

        loadEventHandlers();
    }

    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------

    /**
     * Management of events and triggers
     */
    function loadEventHandlers() {
        // Mod the Age if DOB is selected
        if ($("#Age").length) {
            $("#Age").live('change', function(){
                if (parseInt($(this).val()) > 0) {
                    var d = new Date();
                    year = d.getFullYear() - $(this).val();
                    var dob = year + "-01-01";
                    $("#BirthDate").val(dob);
                    calculateAge();
                    $("#BirthDateEstimated").attr('checked', true);
                } else {
                    $("#BirthDate".val(""));
                    calculateAge();
                }
            });
        }
        $("#BirthDate").live('change', function(){
            calculateAge();
        });
        $("#CountryState.country").live('change', function(){
            $("#PhysicalAddress.country").val($(this).val());
            populate_state_select("PhysicalAddress")
        });
        $("#CountryState.state").live('change', function(){
            $("#PhysicalAddress.state").val($(this).val());
            populate_state_select("PhysicalAddress")
        });
        $("#PhysicalAddress.country").live('change', function(){
            $("#CountryState.country").val($(this).val());
            populate_district_select("CountryState")
        });
        $("#PhysicalAddress.state").live('change', function(){
            $("#CountryState.state").val($(this).val());
            populate_district_select("CountryState")
        });
        $("#patient-base-edit #Anonymous").live('change', function() {
            loadAnonymous();
        });
        $("#patient-base-edit #ClientPatientID").live('change', function() {
            if ($('#patient-base-edit #Anonymous').is(':checked')) {
                $("#patient-base-edit input[id='Surname']").val($("#patient-base-edit #ClientPatientID").val());
            }
        });
        $('#archetypes-fieldname-Gender #Gender').live('change', function(){
            toggleMenstrualStatus(this.value);
        });
        $("input#InsuranceNumber").live('change',function() {
            checkInsuranceNumber(this);
        });
        $("input#InvoiceToInsuranceCompany").live('change',function() {
            checkInvoiceToInsuranceCompany(this);
        });
        $("#PatientAsGuarantor").live('change',function() {
            hide_show_guarantor_fields();
        });
        hide_show_guarantor_fields();
    }

    /**
     * Calculates the age of the patient using the current Birth Date value,
     * and set the result value to 'Age' field. If no Birth Date available or
     * with a non-valid format, restores the value of 'Age' field to empty.
     */
    function calculateAge() {
        var dob = new Date($("#BirthDate").val());
        var now = new Date();
        if (dob!= undefined && dob != null && now>=dob){
            var now = new Date();
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

            if ($("#Age").length) { $("#Age").val(ageyear); }
            $("#AgeSplitted_year").val(ageyear);
            $("#AgeSplitted_month").val(agemonth);
            $("#AgeSplitted_day").val(ageday);

        } else {
            if ($("#Age").length) { $("#Age").val(''); }
            $("#AgeSplitted_year").val('');
            $("#AgeSplitted_month").val('');
            $("#AgeSplitted_day").val('');
        }
        $("#BirthDateEstimated").attr('checked', false);
    }

    /**
     * Shows/Hides the menstrual status
     * @param gender the gender of the patient
     */
    function toggleMenstrualStatus(gender) {
        if ($('#archetypes-fieldname-MenstrualStatus').length){
            if (gender=='female') {
                $('#archetypes-fieldname-MenstrualStatus').show();
            } else {
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
     * Toggles the form between 'regular' and 'Anonymous' patient layout.
     * If the 'Anonymous' checkbox is checked, loads the 'Anonymous' layout,
     * hiding some patient fields (firstname, surname, etc.) and applying
     * default values to them (for instance, using CPID as surname).
     * If the 'Anonymos' checkbox is unchecked, loads the 'regular' layout,
     * showing all fields.
     */
    function loadAnonymous() {
        tohide = ["#patient-base-edit #archetypes-fieldname-Salutation",
                  "#patient-base-edit #archetypes-fieldname-Middleinitial",
                  "#patient-base-edit #archetypes-fieldname-Middlename",
                  "#patient-base-edit #archetypes-fieldname-Firstname",
                  "#patient-base-edit #archetypes-fieldname-Surname",
                  "#patient-base-edit #archetypes-fieldname-AgeSplitted",
                  "#patient-base-edit #archetypes-fieldname-BirthDateEstimated"];

        if ($('#patient-base-edit #Anonymous').is(':checked')) {
            // Hide non desired input fields
            for (i=0;i<tohide.length;i++){
                $(tohide[i]).hide();
            }
            // Set default values
            $("#patient-base-edit #ClientPatientID").attr("required", true);
            $("#patient-base-edit #ClientPatientID_help").before('<span class="required" title="Required">&nbsp;</span>');
            $("#patient-base-edit input[id='Firstname']").val(_("AP"));
            cpid = $("#patient-base-edit #ClientPatientID").val();
            if (cpid && cpid.length > 0) {
                $("#patient-base-edit input[id='Surname']").val(cpid);
            } else {
                $("#patient-base-edit input[id='Surname']").val("-");
            }
            $("#patient-base-edit #archetypes-fieldname-BirthDate").find('span[class="required"]').remove();
            $("#patient-base-edit input[id='BirthDate']").attr("required", false);
            $("#patient-base-edit input[id='BirthDate']").val("");

        } else {
            // Show desired input fields
            for (i=0;i<tohide.length;i++){
                $(tohide[i]+":hidden").show();
            }
            $("#patient-base-edit #archetypes-fieldname-ClientPatientID").find('span[class="required"]').remove();
            $("#patient-base-edit input[id='ClientPatientID']").attr("required", false);
            $("#patient-base-edit input[id='BirthDate']").attr("required", true);
            $("#patient-base-edit #BirthDate_help").before('<span class="required" title="Required">&nbsp;</span>');
        }
    }

    function fillClient(uid) {
        var name = $('#PrimaryReferrer option[value!="'+uid+'"]').remove();
        $('#PrimaryReferrer').val(uid);
    }

    function fillInsuranceCompanyReferrer(rid){
        /**
         * Select the Insurance Company with the rid and remove the other options.
         * @ruid The referrer Insurance Company id.
         */
        var request_data = {
            catalog_name: "bika_setup_catalog",
            portal_type: 'InsuranceCompany',
            id: rid
        };
        window.bika.lims.jsonapi_read(request_data, function (data){
            if (data != null && data['success']== true) {
                var uid = data.objects[0].UID;
                $('#InsuranceCompany option[value!="'+uid+'"]').remove();
                $('#InsuranceCompany').val(uid);
            }
        });
    }

    function checkInsuranceNumber(item){
        /**
         * Disable the 'Send invoices to the insurance company' checkbox if the Insurance number is void
         */
        if ($(item).val().length < 1) {
            $("input#InvoiceToInsuranceCompany").prop('checked', false).unbind("click");
        }
    }

    function checkInvoiceToInsuranceCompany(item){
        /**
         * If 'Send invoices to the insurance company' is checked the Insurance Number becomes mandatory. This
         * function checks if there is an insurance number after the checkbox has been selected. If don't, the checkbox
         * will be disabled.
         */
        if (item.checked && $("input#InsuranceNumber").val().length < 1){
            $(item).prop('checked', false).unbind("click");
        }
    }

    function hide_show_guarantor_fields(){
        /**
         * If the "Patient is the guarantor" checkbox is set, the guarantor's fields are going to be hidden.
         * In the opposite situation, the opposite action is going to happen.
         */
        var fields = $('[data-fieldname*="Guarantor"]').not('#archetypes-fieldname-PatientAsGuarantor');
        var address_widget = $('[id*="GuarantorPostalAddress"]').closest('fieldset');
        if ($("#PatientAsGuarantor").attr('checked')?true:false){
            fields.hide();
            address_widget.hide();
        }
        else {
            fields.show();
            address_widget.show();
        }
    }
}


/**
 * Controller for patient's publication preferences section
 */
function HealthPatientPublicationPrefsEditView() {

    var that = this
    that.publicationprefs_section = $("#archetypes-fieldname-PublicationPreferences");
    that.allowresults_section     = $('#archetypes-fieldname-AllowResultsDistribution');
    that.attachments_section      = $('#archetypes-fieldname-PublicationAttachmentsPermitted');
    that.defaultpubprefs  = $('#DefaultResultsDistribution');
    that.publicationprefs = $('#PublicationPreferences');
    that.allowresults     = $('#AllowResultsDistribution');
    that.attachments      = $('#PublicationAttachmentsPermitted');
    that.opacity = 0.5;

    /**
     * Entry point of PatientPublicationPrefsView
     */
    that.load = function() {

        applyTransitions(false);

        $(that.defaultpubprefs).click(function() {
            applyTransitions(true);
        });

        $(that.attachments).click(function() {
            if ($(that.defaultpubprefs).is(':checked')) {
                // Checkbox state mustn't be changed (readonly mode)
                return false;
            }
        });

        $(that.allowresults).click(function() {
            if ($(that.defaultpubprefs).is(':checked')) {
                // Checkbox state mustn't be changed (readonly mode)
                return false;
            } else {
                applyTransitions(true);
            }
        });
    }

    /**
     * Apply the transitions to input elements and sections.
     * If the 'Inherit default settings' checkbox is checked, fades the
     * elements of the form out and set them as readonly. Otherwhise, set the
     * fields to editable mode and fades them in.
     * Either if 'Inherit default settings' is checked or unchecked, the
     * visibility of the rest of the elements of the form ('Publication
     * preferences' and 'Publications attachment permitted') depends on the
     * status (checked/unchecked) of the 'AllowResultsDistribution' checkbox.
     * @param fade if false, all the transitions will be done as hide/show. If
     *        true, all the transitions will be done as fadeIn(opacity)/fadeOut
     */
    function applyTransitions(fade) {
        fade = fade == null ? false : fade;

        // Set the input fields to read-only
        isdefault = $(that.defaultpubprefs).is(':checked');
        $(that.publicationprefs).attr('readonly', isdefault);
        $(that.attachments).attr('readonly', isdefault);
        $(that.allowresults).attr('readonly', isdefault);

        if (isdefault) {
            allow = fillDefaultPatientPrefs();
        }

        if (fade) {
            if (isdefault) {
                $(that.allowresults_section).fadeTo("slow", that.opacity);
                if (allow) {
                    $(that.publicationprefs_section).fadeTo("slow", that.opacity);
                    $(that.attachments_section).fadeTo("slow", that.opacity);
                } else {
                    $(that.publicationprefs_section).fadeOut("slow");
                    $(that.attachments_section).fadeOut("slow");
                }
            } else {
                $(that.allowresults_section).fadeTo("slow", 1);
                if ($(that.allowresults).is(':checked')) {
                    $(that.publicationprefs_section).fadeTo("slow", 1);
                    $(that.attachments_section).fadeTo("slow", 1);
                } else {
                    $(that.publicationprefs_section).fadeOut("slow");
                    $(that.attachments_section).fadeOut("slow");
                }
            }

        } else {
            if (isdefault) {
                $(that.allowresults_section).fadeTo("fast", that.opacity);
                if (allow) {
                    $(that.publicationprefs_section).fadeTo("fast", that.opacity);
                    $(that.attachments_section).fadeTo("fast", that.opacity);
                } else {
                    $(that.publicationprefs_section).hide();
                    $(that.attachments_section).hide();
                }
            } else {
                // Custom Patients publication preferences
                if (!$(that.allowresults).is(':checked')) {
                    $(that.publicationprefs_section).hide();
                    $(that.attachments_section).hide();
                }
            }
        }
    }

    /**
     * Looks for the patient publication preferences from current Patient's
     * client and fill the form with the data retrieved.
     * @returns true if the patient is allowed to receive the published results
     */
    function fillDefaultPatientPrefs() {
        // Retrieve Patient's publication preferences
        if (!$('#PrimaryReferrer').val()){ return false;}
        $.ajax({
            url: window.portal_url + "/ajax-client",
            type: 'POST',
            async: false,
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'id': guid(),
                   'service': 'getPublicationSettings',
                   'params': JSON.stringify(
                             {'uid':$('#PrimaryReferrer').val()}
                             )},
            dataType: "json",
            success: function(data, textStatus, $XHR){
                if (data['error']==null) {
                    // Fill the form with default values
                    res = data['result'];
                    $(that.allowresults).attr('checked', res['AllowResultsDistributionToPatients']);
                    $(that.attachments).attr('checked', res['PatientPublicationAttachmentsPermitted']);
                    $(that.publicationprefs).find('option').each(function() {
                        $(this).attr('selected', jQuery.inArray(this.value, res['PatientPublicationPreferences']) !=-1);
                    });
                } else {
                    // Error
                    console.log(data['error']);
                }
            }
        });
        return $(that.allowresults).is(':checked');
    }
}

/**
 * Controller for patient's widgets, to remove the last set of data when it isn't empty.
 * Issue HEALTH-178
 */
function HealthPatientGlobalWidgetEditView() {
    var that = this;
    that.load = function() {
        RemoveLastSet();
    }

    function RemoveLastSet() {
        /**
         *Function used to remove the last set of data when it isn't empty.
         */
        $("[class^='records_row_'] .rw_deletebtn").click(function () {
            var nrows = $(this).closest("table tr")
            console.log(nrows);
            if (nrows.length == 1) {
                $(this).closest("tr").find("input").val("");
            }
        });
    }
}

/**
 * Patient's overlay edit view Handler. Used by add buttons to
 * manage the behaviour of the overlay.
 */
function HealthPatientOverlayHandler() {
    var that = this;

    // Needed for bika.lims.loader to register the object at runtime
    that.load = function() {}

    /**
     * Event fired on overlay.onLoad()
     * Hides undesired contents from inside the overlay and also
     * loads additional javascripts still not managed by the bika.lims
     * loader
     */
    that.onLoad = function(event) {

        // Manually remove remarks
        event.getOverlay().find("#archetypes-fieldname-Remarks").remove();

        // Remove menstrual status widget to avoid my suicide
        // with a "500 service internal error"
        event.getOverlay().find("#archetypes-fieldname-MenstrualStatus").remove();

        // Address widget
        $.ajax({
            url: 'bika_widgets/addresswidget.js',
            dataType: 'script',
            async: false
        });
    }
}

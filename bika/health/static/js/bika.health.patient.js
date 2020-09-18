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
     * Entry-point method for PatientEditView
     */
    this.load = function() {

        // Store the visibility and required fields by default, to be able to
        // restore their default values anytime.
        store_field_defaults();

        // It fills out the Insurance Company field.
        var frominsurance = document.referrer.search('/bika_insurancecompanies/') >= 0;
        if (frominsurance){
            // The current Patient add View comes from an insurance companies folder view.
            // Automatically fill the Patient field
            var iid = document.referrer.split("/bika_insurancecompanies/")[1].split("/")[0];
            fillInsuranceCompanyReferrer(iid);
        }

        // Adapt datepicker to current needs
        $("#BirthDate").datepicker("option", "yearRange", "-100:+0" );

        if ($('#patient-base-edit')) {
            loadAnonymous();
        }

        loadEventHandlers();
    }

    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------

    /**
     * Store the default visibility and required values for all fields, by
     * adding default-required and default-visible attributes to each field
     * with their original values
     */
    function store_field_defaults() {
        console.log("Storing default visibility/required");
        $("#patient-base-edit div.field").each(function() {
            var field_id = $(this).attr("id");
            if (!field_id) {
                return;
            }
            var required = $(this).find(".formQuestion .required").length == 1;
            // Note we don't do a :isvisible here, cause the field might belong
            // to a fieldset (tab) that is currently hidden.
            var visible = !($(this).css("display") == "none");
            $(this).attr("default-required", required);
            $(this).attr("default-visible", visible);
        });
    }

    /**
     * Reset the default visibility and required values for all fields, based
     * on the values for attributes default-required and default-visible
     */
    function restore_field_defaults() {
        console.log("Restoring default visibility/required");
        $("#patient-base-edit div.field").each(function() {
            var field_id = $(this).attr("id");
            if (!field_id) {
                return;
            }
            var required = $(this).attr("default-required");
            var visible = $(this).attr("default-visible");
            if (required === 'true') {
                make_required(field_id);
            } else {
                make_unrequired(field_id);
            }
            if (visible === 'true') {
                show_field(field_id);
            } else {
                hide_field(field_id);
            }
        });

        // If the Patient is a Male, do not display Menstrual Status field
        var gender = get_field("Gender");
        if ($(gender).val()!='female') {
            hide_field("MenstrualStatus");
        } else {
            show_field("MenstrualStatus");
        }

        // These are not meant to show up in the main patient base_edit form.
        // they are flagged 'visible' though, so they do show up when requested.
        hide_field("Allergies");
        hide_field("TreatmentHistory");
        hide_field("ImmunizationHistory");
        hide_field("TravelHistory");
        hide_field("ChronicConditions");
    }

    /**
     * Management of events and triggers
     */
    function loadEventHandlers() {
        $("#BirthDate").live('change', function(){
            var estimated = $("#BirthDateEstimated").is(":checked");
            if (estimated == false) {
              calculateAge();
            }
        });
        $("input[id^='AgeSplitted_']").live('change', function(){
            var estimated = $("#BirthDateEstimated").is(":checked");
            if (estimated == true) {
              calculateDoB();
            }
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
        $("#BirthDateEstimated").live("change", function() {
          toggle_dob_estimated();
        });
        toggle_dob_estimated();
        hide_show_guarantor_fields();
    }

    function toggle_dob_estimated() {
      var estimated = $("#BirthDateEstimated").is(":checked");
      if (estimated == true) {
        // DoB estimated. AgeSplitted becomes required
        $("#archetypes-fieldname-BirthDate").hide();
        $("#archetypes-fieldname-AgeSplitted").show();
        make_required("AgeSplitted");
        make_unrequired("BirthDate");

      } else {
        // DoB not estimated. BirthDate becomes required
        $("#archetypes-fieldname-BirthDate").show();
        $("#archetypes-fieldname-AgeSplitted").hide();
        make_required("BirthDate");
        make_unrequired("AgeSplitted");
      }
    }

    /**
     * Returns whether the value passed in is an integer or not
     */
    function isInt(value) {
      return !isNaN(value) &&
             parseInt(Number(value)) == value &&
             !isNaN(parseInt(value, 10));
    }

    /**
     * Calculates the date of birth by using the values for Age
     */
    function calculateDoB() {
      var years = $("#AgeSplitted_year").val();
      var months = $("#AgeSplitted_month").val();
      var days = $("#AgeSplitted_day").val();

      years = isInt(years) ? parseInt(years) : 0;
      months = isInt(months) ? parseInt(months) : 0;
      days = isInt(days) ? parseInt(days) : 0;

      // Calculate in millis (not accurate!)
      total_days = (years * 365.2425) + (months * 30) + days
      millis = total_days * 24 * 60 * 60 * 1000;
      var dateOfBirth = "";
      if (millis > 0) {
        dateOfBirth = new Date(new Date().getTime() - millis);
        dateOfBirth = dateOfBirth.toISOString().slice(0,10);
      }
      $("#BirthDate").val(dateOfBirth);
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
        // Tabs to hide
        var tabs_to_hide = [
            "default",
            "personal",
            "insurance",
            "address",
            "identification",
            "publication-preference",
        ];

        // Fields to hide
        var tohide = [
            "Salutation",
            "Middleinitial",
            "Middlename",
            "Firstname",
            "Surname",
            "ConsentSMS",
        ];

        // Non-required fields
        var nonrequired = [
            "Surname",
            "AgeSplitted_year",
            "AgeSplitted_month",
            "AgeSplitted_day",
            "BirthDate",
            "BirthDateEstimated",
        ];

        // Required fields
        var required = [
            "Firstname",
            "ClientPatientID",
        ];

        if ($('#patient-base-edit #Anonymous').is(':checked')) {
            // Hide tabs
            for (i=0;i<tabs_to_hide.length;i++) {
                $("#fieldsetlegend-"+tabs_to_hide[i]).closest("li.formTab").hide();
            }
            // Hide non desired input fields
            for (i=0;i<tohide.length;i++){
                hide_field(tohide[i]);
            }
            // Make fields non-required
            for (i=0;i<nonrequired.length;i++){
                make_unrequired(nonrequired[i]);
            }
            // Make fields required
            for (i=0;i<required.length;i++){
                make_required(required[i]);
            }
            // Set default values
            $("#patient-base-edit #Firstname").val(_("AP"));
            var cpid = $("#patient-base-edit #ClientPatientID").val();
            if (cpid && cpid.length > 0) {
                $("#patient-base-edit #Surname").val(cpid);
            } else {
                $("#patient-base-edit #Surname").val("");
            }

        } else {
            // Restore tabs visibility
            for (i=0;i<tabs_to_hide.length;i++) {
                $("#fieldsetlegend-"+tabs_to_hide[i]).closest("li.formTab").show();
            }
            // Restore default visibility and required
            restore_field_defaults();
        }
    }

    /**
     * Returns the div element with "field" class that wraps an archetype field
     */
    function get_field(field_id) {
        var field = $('#patient-base-edit #archetypes-fieldname-'+field_id);
        if (!field || field.length < 1) {
            field = $('#patient-base-edit #'+field_id);
            if (!$(field).hasClass(".field")) {
                field = $(field).closest(".field");
            }
        }
        return field;
    }

    /**
     * Set a field as required.
     * field_id can be either the id of the div element .field that wraps the
     * input field or the id of any of the elements it contains
     */
    function make_required(field_id) {
        console.log("Set required: " + field_id);
        var field = get_field(field_id);
        $(field).find(".formQuestion .required").remove();
        var lbl = $(field).find(".formQuestion");
        if (lbl && lbl.length > 0) {
            var span = '<span class="required" title="Required"></span>';
            var field_help = $(lbl).find(".help-block");
            if (field_help && field_help.length > 0) {
                $(field_help).before(span);
            } else {
                $(lbl[0]).html($(lbl[0]).html() + span);
            }
        }
    }

    /**
     * Set a field as unrequired.
     * field_id can be either the id of the div element .field that wraps the
     * input(s) field(s) or the id of any of the elements it contains
     */
    function make_unrequired(field_id) {
        console.log("Set unrequired: "+field_id);
        var field = get_field(field_id);
        $(field).find(".formQuestion .required").remove();
    }

    /**
     * Hides a field.
     * field_id can be either the id of the div element .field that wraps the
     * input(s) field(s) or the id of any of the elements it contains
     */
    function hide_field(field_id) {
        console.log("Hide field: "+field_id);
        var field = get_field(field_id);
        field.hide();
    }

    /**
     * Displays a field.
     * field_id can be either the id of the div element .field that wraps the
     * input(s) field(s) or the id of any of the elements it contains
     */
    function show_field(field_id) {
        console.log("Show field: "+field_id);
        var field = get_field(field_id);
        field.show();
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

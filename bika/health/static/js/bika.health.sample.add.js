/**
 * Controller class for AnalysisRequest add view
 */
function HealthSampleAddView() {

    var that = this;

    /**
     * Entry-point method for SampleAddView
     */
    this.load = function () {
        datafilled = false;
        frompatient = document.referrer.search('/patients/') >= 0;
        fromsamples = window.location.href.search('/samples/') >=0;

        if (frompatient) {
            // The current Sample add View comes from a patient Sample folder
            // view. Automatically fill the Client and Patient fields and set
            // them  as readonly.
            pid = document.referrer.split("/patients/")[1].split("/")[0];
            datafilled = fillDataFromPatient(pid);
        } else if(fromsamples){
          $('input[id^="Client-"]').bind(
                "selected paste blur change",
                function () {
                    colposition = get_samplenum(this);
                    if (colposition == undefined){
                        // we are on the specific health template
                        colposition = 0;}
                        resetPatientData(colposition)
                        filterComboSearches();
                }
            );
        }

        // Filter ComboSearches is important here even patient is not found
        // because we are under patient's client folder.
        // Do not let other clients have Samples in this context!!!
        if (!datafilled || frompatient) {
            // The current Sample Add View doesn't come from a
            // patient or data autofilling failed. Handle event firing when
            // Patient or ClientPatientID fields change.
            $('input[id^="ClientPatientID-"]').bind("selected paste blur change", function () {
                colposition = get_samplenum(this);
                if (colposition == undefined){
                    // we are on the specific health template
                    colposition = 0}
                uid = $("#" + this.id + "_uid").val();
                loadPatient(uid, colposition);
            });

            $('input[id^="Patient-"]').bind("selected paste blur change", function () {
                colposition = get_samplenum(this);
                if (colposition == undefined){
                    // we are on the specific health template
                    colposition = 0}
                uid = $("#" + this.id + "_uid").val();
                loadClientPatientID(uid, colposition);
            });

            // Patient and PatientCID combos must only show the
            // records from the current client
            filterComboSearches();
        }
    };

    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------
    /**
     * Searches a patient using the Patient UID from Client Patient Input.
     * If found, fill the Patient's input fields from the same Sample add
     * column.
     *  If no patient found, set the values to Anonymous.
     * @param id Patient UID
     * @param colposition Sample add column position
     */
    function loadPatient(id, colposition) {
        if (id != '') {
            $.ajax({
                url: window.portal_url + "/getpatientinfo",
                type: 'POST',
                data: {
                    '_authenticator': $('input[name="_authenticator"]').val(),
                    'PatientUID': id
                },
                dataType: "json",
                success: function (data, textStatus, $XHR) {
                    if (data['PatientUID'] != '') {
                        $("#Patient-" + colposition)
                            .val(data['PatientFullname'])
                            .attr('uid', data['PatientUID'])
                            .combogrid("option", "disabled", false);
                        $("#Patient-" + colposition + "_uid").val(data['PatientUID']);
                    } else {
                        // No patient found. Set anonymous patient
                        $("#Patient-" + colposition)
                            .val(_('Anonymous'))
                            .attr('uid', 'anonymous');
                        $("#Patient-" + colposition + "_uid").val('anonymous');
                    }
                    if (data['ClientUID'] != '') {
                        $("#Client-" + colposition)
                            .val(data['ClientTitle'])
                            .attr('uid', data['ClientUID'])
                            .combogrid("option", "disabled", false);
                        $("#Client-" + colposition + "_uid").val(data['ClientUID']);
                    }
                }
            });
        } else {
            // Empty client patient id. Reset patient fields
            $("#Patient-" + colposition)
                .val('').attr('uid', '').combogrid("option", "disabled", false);
            $("#Patient-" + colposition + "_uid").val('');
        }
    }

    /**
     * Searches a patient using the Patient UID. If found, fill the Client
     * Patient
     * ID from the same Sample add column. If no patient found, set the value
     * to empty.
     * @param uid Patient UID
     * @param colposition Sample add column position
     */
    function loadClientPatientID(uid, colposition) {
        if (uid == 'anonymous') {
            // Anonymous Patient, do nothing.
            return;
        }
        if (uid != '') {
            $.ajax({
                url: window.portal_url + "/getpatientinfo",
                type: 'POST',
                data: {
                    '_authenticator': $('input[name="_authenticator"]').val(),
                    'PatientUID': uid
                },
                dataType: "json",
                success: function (data, textStatus, $XHR) {
                    $("#ClientPatientID-" + colposition).val(data['ClientPatientID']);
                    $("#ClientPatientID-" + colposition).attr('uid', uid);
                    $("#ClientPatientID-" + colposition + "_uid").val(uid);
                    $("#Client-" + colposition)
                        .val(data['ClientTitle'])
                        .attr('uid', data['ClientUID'])
                        .combogrid("option", "disabled", false);
                    $("#Client-" + colposition + "_uid").val(data['ClientUID']);
                }
            });
        } else {
            // Empty client patient id. Reset patient fields
            $("#ClientPatientID-" + colposition).val('');
            $("#ClientPatientID-" + colposition).attr('uid', '');
            $("#ClientPatientID-" + colposition + "_uid").val('');
        }
    }

    /**
     * Searches a patient using the Patient ID. If found, fill the Client,
     * Patient,
     * and ClientPatientID fields and set them as readonly for all columns.
     * If no patient found, does nothing.
     * @param id Patient ID
     * @return true if the patient was found and input fields were filled.
     */
    function fillDataFromPatient(id) {
        var succeed = false;
        if (id != '') {
            $.ajax({
                url: window.portal_url + "/getpatientinfo",
                type: 'POST',
                data: {
                    '_authenticator': $('input[name="_authenticator"]').val(),
                    'PatientID': pid,
                },
                dataType: "json",
                async: false,
                success: function (data, textStatus, $XHR) {
                    if (data['PatientUID'] != '') {
                        $(".dynamic-field-label").remove();
                        fillPatientData(0, data);
                    }
                }
            });
            return $("#Patient-0").attr('uid') != '';
        }
        return false;
    }

    function filterComboSearches() {
        // Only allow the selection of patients, and CPIDs
        // from the current client
        for (var col = 0; col < parseInt($("#obj_count").val()); col++) {
            clientuid = $($("tr[fieldname='Client'] td[samplenum='" + col + "'] input")[1]).attr("value");

            // Patient searches
            element = $("#Patient-" + col);
            if (element.length > 0) {
                filter_combogrid(element[0], "getPrimaryReferrerUID", clientuid);
            }

            // CPID searches
            element = $("#ClientPatientID-" + col);
            if (element.length > 0) {
                filter_combogrid(element[0], "getPrimaryReferrerUID", clientuid);
            }
        }
    }

    function fillPatientData(col, data) {
        $("#Client-" + col).val(data['ClientTitle']);
        $("#Client-" + col).attr('uid', data['ClientUID']);
        $("#Client-" + col).attr('cid', data['ClientSysID']);
        $("#Client-" + col + "_uid").val(data['ClientUID']);

        $("#Patient-" + col).val(data['PatientFullname']);
        $("#Patient-" + col).attr('uid', data['PatientUID']);
        $("#Patient-" + col + "_uid").val(data['PatientUID']);

        $("#ClientPatientID-" + col).val(data['ClientPatientID']);
        $("#ClientPatientID-" + col).attr('uid', data['PatientUID']);
        $("#ClientPatientID-" + col + "_uid").val(data['PatientUID']);
    }

    function resetPatientData(col) {
        // Empty client patient id. Reset patient fields
        $("#Patient-" + col).val('');
        $("#Patient-" + col).attr('uid', '');
        $("#Patient-" + col + "_uid").val('');
        $("#Patient-" + col).combogrid("option", "disabled", false);

        $("#ClientPatientID-" + col).val('');
        $("#ClientPatientID-" + col).attr('uid', '');
        $("#ClientPatientID-" + col + "_uid").val('');
        $("#ClientPatientID-" + col).combogrid("option", "disabled", false);

        frompatient = document.referrer.search('/patients/') >= 0;

        if (frompatient) {
            // The current Sample add View comes from a patient AR folder view.
            // Automatically fill the Client and Patient fields and set them
            // as readonly.
            pid = document.referrer.split("/patients/")[1].split("/")[0];
            datafilled = fillDataFromPatient(pid);

            // The Patient and PatientCID combos must only show the
            // records from the current client
            filterComboSearches();

        }
    }
    function get_samplenum(element) {
        // Should be able to deduce the samplenum of any form element
        var samplenum
        // Most Sample schema field widgets have [samplenum=<samplenum>] on their parent TD
        samplenum = $(element).parents("[samplenum]").attr("samplenum")
        if (samplenum) {
            return samplenum
        }
        console.error("No samplenum found for element " + element)
    }

    /**
     * Apply or modify a query filter for a reference widget.
     * This will set the options, then re-create the combogrid widget
     * with the new filter key/value.
     */
    function filter_combogrid(element, filterkey, filtervalue, querytype) {
        /* Apply or modify a query filter for a reference widget.
         *
         *  This will set the options, then re-create the combogrid widget
         *  with the new filter key/value.
         *
         *  querytype can be 'base_query' or 'search_query'.
         */
        if (!$(element).is(':visible')) {
            return
        }
        if (!querytype) {
            querytype = 'base_query'
        }
        var query = $.parseJSON($(element).attr(querytype))
        query[filterkey] = filtervalue
        $(element).attr(querytype, $.toJSON(query))
        var options = $.parseJSON($(element).attr("combogrid_options"))
        options.url = window.location.href.split("/sample_add")[0] + "/" + options.url
        options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val()
        options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name")
        if (querytype == 'base_query') {
            options.url = options.url + "&base_query=" + $.toJSON(query)
            options.url = options.url + "&search_query=" + $(element).attr("search_query")
        }
        else {
            options.url = options.url + "&base_query=" + encodeURIComponent($(element).attr("base_query"))
            options.url = options.url + "&search_query=" + encodeURIComponent($.toJSON(query))
        }
        options.url = options.url + "&colModel=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).colModel)
        options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options"))['search_fields'])
        options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options"))['discard_empty'])
        options.force_all = "false"
        $(element).combogrid(options)
        $(element).attr("search_query", "{}")
    }
}

/**
 * Controller class for AnalysisRequest add view
 */
function HealthAnalysisRequestAddView() {

    var that = this;

    /**
     * Entry-point method for AnalysisRequestAddView
     */
    this.load = function () {
        datafilled = false;
        frombatch = window.location.href.search('/batches/') >= 0;
        frompatient = document.referrer.search('/patients/') >= 0;
        fromars = window.location.href.search('/analysisrequests/') >=0;

        if (frombatch) {
            // The current AR add View comes from a batch. Automatically fill
            // the Client, Patient and Doctor fields and set them as readonly.
            batchid = window.location.href.split("/batches/")[1].split("/")[0];
            datafilled = fillDataFromBatch(batchid);

        } else if (frompatient) {
            // The current AR add View comes from a patient AR folder view.
            // Automatically fill the Client and Patient fields and set them
            // as readonly.
            pid = document.referrer.split("/patients/")[1].split("/")[0];
            datafilled = fillDataFromPatient(pid);
        } else if(fromars){
          $('input[id^="Client-"]').bind("selected paste blur change", function () {
              colposition = get_arnum(this);
              if (colposition == undefined){
                  // we are on the specific health template
                  colposition = 0}
              resetPatientData(colposition)
              filterComboSearches();
          });
        }

        // Filter ComboSearches is important here even patient is not found
        // because we are under patient's client folder.
        // Do not let other clients have ARs in this context!!!
        if (!datafilled || frompatient) {
            // The current AR Add View doesn't come from a batch nor patient or
            // data autofilling failed. Handle event firing when Patient or
            // ClientPatientID fields change.
            $('input[id^="ClientPatientID-"]').bind("selected paste blur change", function () {
                colposition = get_arnum(this);
                if (colposition == undefined){
                    // we are on the specific health template
                    colposition = 0}
                uid = $("#" + this.id + "_uid").val();
                loadPatient(uid, colposition);
                checkClientContacts();
            });

            $('input[id^="Patient-"]').bind("selected paste blur change", function () {
                colposition = get_arnum(this);
                if (colposition == undefined){
                    // we are on the specific health template
                    colposition = 0}
                uid = $("#" + this.id + "_uid").val();
                loadClientPatientID(uid, colposition);
                checkClientContacts();
            });

            // When the user selects an earlier sample (from storage say) and creates a
            // secondary AR for it, the Patient field should also be looked up and
            // uneditable.
            // See https://github.com/bikalabs/bika.health/issues/100
            $('input[id^="Sample-"]').bind("selected paste blur", function () {
                colposition = get_arnum(this);
                if (colposition == undefined){
                    // we are on the specific health template
                    colposition = 0}
                uid = $("#" + this.id + "_uid").val();
                loadPatientFromSample(uid, colposition);
                checkClientContacts();
            });

            // The Batch, Patient and PatientCID combos must only show the
            // records from the current client
            filterComboSearches();
        }


        // Check if the current selected client has contacts. If client has no
        // contacts, prevent from saving the AR and inform the user
        checkClientContacts();
    };

    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------
    /**
     * Searches a patient using the Patient UID from Client Patient Input.
     * If found, fill the Patient's input fields from the same AR add column.
     *  If no patient found, set the values to Anonymous.
     * @param id Patient UID
     * @param colposition AR add column position
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
     * Searches a patient using the Patient UID. If found, fill the Client Patient
     * ID from the same AR add column. If no patient found, set the value to empty.
     * @param uid Patient UID
     * @param colposition AR add column position
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
     * Searches a batch using the Batch ID. If found, fill the Client, Patient,
     * ClientPatientID and Doctor fields and set them as readonly for all columns.
     * If no batch found, does nothing.
     * @param id Batch ID
     * @return true if the batch was found and input fields were filled.
     */
    function fillDataFromBatch(id) {
        if (id !== '') {
            $.ajax({
                url: window.portal_url + "/batches/" + batchid + "/getBatchInfo",
                type: 'POST',
                data: {'_authenticator': $('input[name="_authenticator"]').val()},
                dataType: "json",
                async: false,
                success: function (data, textStatus, $XHR) {
                    if (data.PatientUID !== '') {
                        $(".dynamic-field-label").remove();
                        for (var col = 0; col < parseInt($("#ar_count").val()); col++) {
                            $("#Client-" + col).val(data.ClientTitle);
                            $("#Client-" + col).attr('uid', data.ClientUID);
                            $("#Client-" + col).attr('cid', data.ClientSysID);
                            $("#Client-" + col + "_uid").val(data.ClientUID);

                            $("#Patient-" + col).val(data.PatientTitle);
                            $("#Patient-" + col).attr('uid', data.PatientUID);
                            $("#Patient-" + col + "_uid").val(data.PatientUID);

                            $("#Doctor-" + col).val(data.DoctorTitle);
                            $("#Doctor-" + col).attr('uid', data.DoctorUID);
                            $("#Doctor-" + col + "_uid").val(data.DoctorUID);

                            $("#ClientPatientID-" + col).val(data.ClientPatientID);
                            $("#ClientPatientID-" + col + "_uid").val(data.PatientUID);

                            // Hide the previous fields and replace them by labels
                            $("#Client-" + col).hide();
                            $("#Patient-" + col).hide();
                            $('#Patient_addbutton').hide();
                            $("#Doctor-" + col).hide();
                            $('#Doctor_addbutton').hide();
                            $("#ClientPatientID-" + col).hide();
                            $("#Client-" + col).after("<span class='dynamic-field-label'>" + $("#Client-" + col).val() + "</span>");
                            $("#Patient-" + col).after("<span class='dynamic-field-label'>" + $("#Patient-" + col).val() + "</span>");
                            $("#Doctor-" + col).after("<span class='dynamic-field-label'>" + $("#Doctor-" + col).val() + "</span>");
                            $("#ClientPatientID-" + col).after("<span class='dynamic-field-label'>" + $("#ClientPatientID-" + col).val() + "</span>");

                            // Contact searches
                            element = $("#Contact-" + col)[0];
                            filter_combogrid(element, "getParentUID", data.ClientUID);
                        }
                        return true;
                    }
                }
            });
        }
        return false;
    }

    /**
     * Searches a patient using the Patient ID. If found, fill the Client, Patient,
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
        // Only allow the selection of batches, patients, contacts and CPIDs
        // from the current client
        for (var col = 0; col < parseInt($("#ar_count").val()); col++) {
            clientuid = $($("tr[fieldname='Client'] td[arnum='" + col + "'] input")[1]).attr("value");

            // Batch searches
            element = $("#Batch-" + col);
            if (element.length > 0){
                filter_combogrid(element[0], "getClientUID", clientuid);
            }

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

            // Contact searches
            element = $("#Contact-" + col);
            if (element.length > 0) {
                filter_combogrid(element[0], "getParentUID", clientuid);
            }
        }
    }

    /**
     * Checks if the current client has contacts. If no contacts, show a message
     * informing the user
     */
    function checkClientContacts() {
        cids = new Array();
        // Check if comes from a Client view
        if (window.location.href.search("/clients/") >= 0) {
            cid = window.location.href.split("/clients/")[1].split("/")[0];
            cids.push(cid);
        }
        // Populate an array of cids first in order to avoid excessive request
        // calls via ajax. Must of the cases will have the same client for all
        // columns.
        for (var col = 0; col < parseInt($("#ar_count").val()); col++) {
            cid = $("#Client-" + col).attr('cid');
            if (cid != null && cid != '' && $.inArray(cid, cids) < 0) {
                cids.push(cid);
            }
        }
        $('div[id="contactsempty_alert"]').remove();
        for (var i = 0; i < cids.length; i++) {
            // Retrieve the client and check if has contacts
            cid = cids[i];
            $.ajax({
                url: window.portal_url + "/clients/" + cid + "/getClientInfo",
                type: 'POST',
                async: false,
                data: {'_authenticator': $('input[name="_authenticator"]').val()},
                dataType: "json",
                success: function (data, textStatus, $XHR) {
                    if (data['ContactUIDs'] == '' || data['ContactUIDs'].length == 0) {
                        $('table.analysisrequest').before("<div id='contactsempty_alert' class='alert'>"
                        + _("Client contact required before request may be submitted")
                        + ". <a href='" + window.portal_url + "/clients/" + cid + "/contacts'>"
                        + _("Add contacts") + " " + data['ClientTitle']
                        + "</a></div>");
                    }
                }
            });
        }
    }

    /**
     * Loads the patient from the selected sample when the user creates
     * a secondary AR for it. Sets the Patient-related fields as readonly.
     * If id is empty or null, the Patient fields gets reseted and editable.
     * @param uid Sample UID
     * @param colposition AR add column position
     * @return true if the sample has been found and patient fields has been set.
     * Otherwise, returns false
     */
    function loadPatientFromSample(uid, colposition) {
        var col = colposition;
        if (uid != null && uid != '') {
            $.ajax({
                url: window.portal_url + "/getsamplepatient",
                type: 'POST',
                data: {
                    '_authenticator': $('input[name="_authenticator"]').val(),
                    'uid': uid,
                },
                dataType: "json",
                async: false,
                success: function (data, textStatus, $XHR) {
                    if (data['PatientID'] != '') {
                        fillPatientData(col, data);
                    } else {
                        resetPatientData(col);
                    }
                }
            });
        } else {
            resetPatientData(col);
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

        // Only allow the selection of batches from this patient
        element = $("#Batch-" + col);
        filter_combogrid(element[0], "getPatientUID", data['PatientUID']);

        // Contact searches
        element = $("#Contact-" + col);
        filter_combogrid(element[0], "getParentUID", data['ClientUID']);
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

        frombatch = window.location.href.search('/batches/') >= 0;
        frompatient = document.referrer.search('/patients/') >= 0;

        if (frombatch) {
            // The current AR add View comes from a batch. Automatically fill
            // the Client, Patient and Doctor fields and set them as readonly.
            batchid = window.location.href.split("/batches/")[1].split("/")[0];
            datafilled = fillDataFromBatch(batchid);

            // The Batch, Patient and PatientCID combos must only show the
            // records from the current client
            filterComboSearches();

            // Check if the current selected client has contacts. If client has no
            // contacts, prevent from saving the AR and inform the user
            checkClientContacts();

        } else if (frompatient) {
            // The current AR add View comes from a patient AR folder view.
            // Automatically fill the Client and Patient fields and set them
            // as readonly.
            pid = document.referrer.split("/patients/")[1].split("/")[0];
            datafilled = fillDataFromPatient(pid);

            // The Batch, Patient and PatientCID combos must only show the
            // records from the current client
            filterComboSearches();

            // Check if the current selected client has contacts. If client has no
            // contacts, prevent from saving the AR and inform the user
            checkClientContacts();

        } else {

            // Clear the batches selection from this patient
            element = $("#Batch-" + col);
            filter_combogrid(element[0], "getPatientUID", "");

            // Contact searches
            element = $("#Contact-" + col);
            filter_combogrid(element[0], "getParentUID", "");
        }
    }
    function get_arnum(element) {
        // Should be able to deduce the arnum of any form element
        var arnum
        // Most AR schema field widgets have [arnum=<arnum>] on their parent TD
        arnum = $(element).parents("[arnum]").attr("arnum")
        if (arnum) {
            return arnum
        }
        // analysisservice checkboxes have an ar.<arnum> class on the parent TD
        var td = $(element).parents("[class*='ar\\.']")
        if (td.length > 0) {
            var arnum = $(td).attr("class").split('ar.')[1].split()[0]
            if (arnum) {
                return arnum
            }
        }
        console.error("No arnum found for element " + element)
    }

    /**
     * Apply or modify a query filter for a reference widget.
     * This will set the options, then re-create the combogrid widget
     * with the new filter key/value.
     * Delegates the action to window.bika.lims.AnalysisRequestAddByCol.filter_combogrid
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
        options.url = window.location.href.split("/ar_add")[0] + "/" + options.url
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

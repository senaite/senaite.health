/**
 * Controller class for AnalysisRequest add view
 */
function AnalysisRequestAddView() {
    
    var that = this;
    
    // ------------------------------------------------------------------------
    // PUBLIC ACCESSORS
    // ------------------------------------------------------------------------
    
    
    // ------------------------------------------------------------------------
    // PUBLIC FUNCTIONS
    // ------------------------------------------------------------------------

    /**
     * Entry-point method for AnalysisRequestAddView
     */
    this.load = function() {
        datafilled = false;
        frombatch = window.location.href.search('batches/') > 0;
        frompatient = document.referrer.search('/patients/') >= 0;
        
        if (frombatch) {
            // The current AR add View comes from a batch. Automatically fill
            // the Client, Patient and Doctor fields and set them as readonly.
            batchid = window.location.href.split("batches")[1].split("/")[1];
            datafilled = fillDataFromBatch(batchid);
            
        } else if (frompatient) {
            // The current AR add View comes from a patient AR folder view.
            // Automatically fill the Client and Patient fields and set them
            // as readonly.
            pid = document.referrer.split("/patients/")[1].split("/")[0];
            datafilled = fillDataFromPatient(pid);
        }

        if (!datafilled) {
            // The current AR Add View doesn't come from a batch nor patient or
            // data autofilling failed. Handle event firing when Patient or 
            // ClientPatientID fields change.
            $('[id$="_ClientPatientID"]').bind("selected paste blur", function() {
                colposition = this.id.split("_")[1]
                id = $(this).val()
                loadPatient(id, colposition);
            });

            $('[id$="_Patient"]').bind("selected", function() {
                colposition = this.id.split("_")[1]
                uid = $(this).attr('uid');
                loadClientPatientID(uid, colposition);
            });

            // The Batch, Patient and PatientCID combos must only show the
            // records from the current client
            filterComboSearches();
        }
    }
    
    // ------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    // ------------------------------------------------------------------------
    /**
     * Searches a patient using the Patient UID. If found, fill the Patient's input
     * fields from the same AR add column. If no patient found, set the values to
     * Anonymous.
     * @param id Client Patient ID
     * @param colposition AR add column position
     */
    function loadPatient(id, colposition) {
        if (id != '') {
            $.ajax({
                url : window.portal_url + "/getpatientinfo",
                type : 'POST',
                data : {
                    '_authenticator' : $('input[name="_authenticator"]').val(),
                    'ClientPatientID' : id
                },
                dataType : "json",
                success : function(data, textStatus, $XHR) {
                    if (data['PatientUID'] != '') {
                        $("#ar_" + colposition + "_Patient").val(data['PatientFullname']);
                        $("#ar_" + colposition + "_Patient").attr('uid',data['PatientUID']);
                        $("#ar_" + colposition + "_Patient_uid").val(data['PatientUID']);
                        $("#ar_" + colposition + "_Patient").attr("readonly", false);
                        $("#ar_" + colposition + "_Patient").combogrid("option", "disabled", false);
                    } else {
                        // No patient found. Set anonymous patient
                        $("#ar_" + colposition + "_Patient").val(_('Anonymous'));
                        $("#ar_" + colposition + "_Patient").attr('uid','anonymous');
                        $("#ar_" + colposition + "_Patient_uid").val('anonymous');
                        $("#ar_" + colposition + "_Patient").attr("readonly", true);
                        $("#ar_" + colposition + "_Patient").combogrid("option", "disabled", true);
                    }
                }
            });
        } else {
            // Empty client patient id. Reset patient fields
            $("#ar_" + colposition + "_Patient").val('');
            $("#ar_" + colposition + "_Patient").attr('uid', '');
            $("#ar_" + colposition + "_Patient_uid").val('');
            $("#ar_" + colposition + "_Patient").attr("readonly", false);
            $("#ar_" + colposition + "_Patient").combogrid("option", "disabled", false);
        }
    }

    /**
     * Searches a patient using the Patient UID. If found, fill the Client Patient
     * ID from the same AR add column. If no patient found, set the value to empty.
     * @param uid Patient UID
     * @param colposition AR add column position
     */
    function loadClientPatientID(uid, colposition) {
        if (uid != '') {
            $.ajax({
                url : window.portal_url + "/getpatientinfo",
                type : 'POST',
                data : {
                    '_authenticator' : $('input[name="_authenticator"]').val(),
                    'PatientUID' : uid
                },
                dataType : "json",
                success : function(data, textStatus, $XHR) {
                    $("#ar_" + colposition + "_ClientPatientID").val(data['ClientPatientID']);
                    $("#ar_" + colposition + "_ClientPatientID").attr('uid', uid);
                    $("#ar_" + colposition + "_ClientPatientID_uid").val(uid);
                }
            });
        } else {
            // Empty client patient id. Reset patient fields
            $("#ar_" + colposition + "_ClientPatientID").val('');
            $("#ar_" + colposition + "_ClientPatientID").attr('uid', '');
            $("#ar_" + colposition + "_ClientPatientID_uid").val('');
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
        if (id != '') {
            $.ajax({
                url: window.portal_url + "/batches/" + batchid + "/getBatchInfo",
                type: 'POST',
                data: {'_authenticator': $('input[name="_authenticator"]').val()},
                dataType: "json",
                async: false,
                success: function(data, textStatus, $XHR){
                    if (data['PatientUID'] != '') {
                        for (var col=0; col<parseInt($("#col_count").val()); col++) {
                            $("#ar_" + col +"_Client").val(data['ClientTitle']);
                            $("#ar_" + col +"_Client").attr('uid',data['ClientUID']);
                            $("#ar_" + col +"_Client_uid").val(data['ClientUID']);
                            $("#ar_" + col +"_Client").attr('readonly', true);
                            $("#ar_" + col +"_Client").combogrid("option", "disabled", true);
                            
                            $("#ar_" + col +"_Patient").val(data['PatientTitle']);
                            $("#ar_" + col +"_Patient").attr('uid',data['PatientUID']);
                            $("#ar_" + col +"_Patient_uid").val(data['PatientUID']);
                            $("#ar_" + col +"_Patient").attr('readonly', true);
                            $("#ar_" + col +"_Patient").combogrid("option", "disabled", true);
        
                            $("#ar_" + col +"_Doctor").val(data['DoctorTitle']);
                            $("#ar_" + col +"_Doctor").attr('uid',data['DoctorUID']);
                            $("#ar_" + col +"_Doctor_uid").val(data['DoctorUID']);
                            $("#ar_" + col +"_Doctor").attr('readonly', true);
                            $("#ar_" + col +"_Doctor").combogrid("option", "disabled", true);
        
                            $("#ar_" + col +"_ClientPatientID").val(data['ClientPatientID']);
                            $("#ar_" + col +"_ClientPatientID").attr('readonly', true);
                            $("#ar_" + col +"_ClientPatientID").combogrid("option", "disabled", true);
                        }
                        succeed = true;
                    }
                }
            });
            return $("#ar_0_Patient").attr('uid',data['PatientUID']) != '';
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
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'PatientID': pid,},
                dataType: "json",
                async: false,
                success: function(data, textStatus, $XHR){
                    if (data['PatientUID'] != '') {
                        for (var col=0; col<parseInt($("#col_count").val()); col++) {
                            $("#ar_" + col +"_Client").val(data['ClientTitle']);
                            $("#ar_" + col +"_Client").attr('uid',data['ClientUID']);
                            $("#ar_" + col +"_Client_uid").val(data['ClientUID']);
                            $("#ar_" + col +"_Client").attr('readonly', true);
                            $("#ar_" + col +"_Client").combogrid("option", "disabled", true );
                            
                            $("#ar_" + col +"_Patient").val(data['PatientFullname']);
                            $("#ar_" + col +"_Patient").attr('uid',data['PatientUID']);
                            $("#ar_" + col +"_Patient_uid").val(data['PatientUID']);
                            $("#ar_" + col +"_Patient").attr('readonly', true);
                            $("#ar_" + col +"_Patient").combogrid("option", "disabled", true );
            
                            $("#ar_" + col +"_ClientPatientID").val(data['ClientPatientID']);
                            $("#ar_" + col +"_ClientPatientID").attr('uid',data['PatientUID']);
                            $("#ar_" + col +"_ClientPatientID_uid").val(data['PatientUID']);
                            $("#ar_" + col +"_ClientPatientID").attr('readonly', true);
                            $("#ar_" + col +"_ClientPatientID").combogrid("option", "disabled", true );
                            
                            // Only allow the selection of batches from this patient
                            element = $("#ar_" + col + "_Batch")
                            base_query=$.parseJSON($(element).attr("base_query"));
                            base_query['getPatientUID'] = data['PatientUID'];
                            applyComboFilter(element, base_query);
                        }
                    }
                }
            });
            return $("#ar_0_Patient").attr('uid',data['PatientUID']) != '';
        }
        return false;
    }

    function filterComboSearches() {
        // Only allow the selection of batches, patients and CPIDs from the
        // current client
        for (var col=0; col<parseInt($("#col_count").val()); col++) {
            clientuid = $("#ar_" + col + "_Client_uid").val();

            // Batch searches
            element = $("#ar_" + col + "_Batch")
            base_query=$.parseJSON($(element).attr("base_query"));
            base_query['getClientUID'] = clientuid;
            applyComboFilter(element, base_query);

            // Patient searches
            element = $("#ar_" + col + "_Patient")
            base_query=$.parseJSON($(element).attr("base_query"));
            base_query['getPrimaryReferrerUID'] = clientuid;
            applyComboFilter(element, base_query);

            // CPID searches
            element = $("#ar_" + col + "_ClientPatientID")
            base_query=$.parseJSON($(element).attr("base_query"));
            base_query['getPrimaryReferrerUID'] = clientuid;
            applyComboFilter(element, base_query);
        }
    }

    function applyComboFilter(element, base_query) {
        options = $.parseJSON($(element).attr("combogrid_options"));
        options.url = window.location.href.split("/ar_add")[0] + "/" + options.url
        options.url = options.url + '?_authenticator=' + $('input[name="_authenticator"]').val();
        options.url = options.url + '&catalog_name=' + $(element).attr('catalog_name');
        options.url = options.url + '&base_query=' + $.toJSON(base_query);
        options.url = options.url + '&search_query=' + $(element).attr('search_query');
        options.url = options.url + '&colModel=' + $.toJSON( $.parseJSON($(element).attr('combogrid_options'))["colModel"] );
        options.url = options.url + '&search_fields=' + $.toJSON($.parseJSON($(element).attr('combogrid_options'))["search_fields"]);
        options.url = options.url + '&discard_empty=' + $.toJSON($.parseJSON($(element).attr('combogrid_options'))["discard_empty"]);
        options['force_all']='false';
        $(element).combogrid(options);
        $(element).addClass("has_combogrid_widget");
        $(element).attr('search_query', '{}');
    }
}

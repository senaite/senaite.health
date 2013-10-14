/**
 * Controller class for Batch readonly view
 */
function BatchViewView() {

    /**
     * Entry-point method for BatchViewView
     */
    this.load = function() {
        
        // These look silly in the edit screen under "Additional Notes"
        $('div[id^="archetypes-fieldname-Remarks-"]').remove();
    }
}

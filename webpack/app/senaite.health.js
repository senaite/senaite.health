/* senaite.health main JS bundle */

document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE HEALTH JS LOADED ***");

  /* Initialize i18n JS message factory */
  window.i18n.loadCatalog("senaite.health");
  window._h = window.i18n.MessageFactory("senaite.health");

});

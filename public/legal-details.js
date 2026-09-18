// The only place the legal details live. Both privacy.html and terms.html read
// from here, so filling these in once fills in both pages.
//
// entity   Your legal name. If there is no company, that is your own name,
//          trading as StreetSweeperCustoms. It must match the name Stripe has, because
//          that is the name on your customers' card statements and receipts.
// address  A real postal address. "Online only" is not a category consumer law
//          recognises, and selling at a distance in the EU and UK requires a
//          geographic address. It does not have to be your home -- a virtual
//          office or mail-forwarding address is the usual answer.
// email    An address you will actually read. Data requests and complaints
//          arrive here, and both PDPA and GDPR expect a reply.
// law      The country you actually trade from. Naming one you have no
//          presence in is worse than naming none.
window.CRF_LEGAL = {
  entity:  "Eoin McGee trading as StreetSweeperCustoms",
  address: "Room 208, Sunset Boulevard 2, Banglamung, Pattaya, Chonburi 20150, Thailand",
  email:   "eoinmcgee1993@gmail.com",
  law:     "Thailand",
};

// Anything still blank is called out on the page rather than left as a silent
// gap, so these pages cannot go live half-finished by accident.
document.addEventListener("DOMContentLoaded", () => {
  const missing = [];
  document.querySelectorAll("[data-legal]").forEach(el => {
    const key = el.getAttribute("data-legal");
    const val = ((window.CRF_LEGAL || {})[key] || "").trim();
    if(val){
      el.textContent = val;
    } else {
      el.textContent = "[" + key.toUpperCase() + " NOT SET]";
      el.style.color = "var(--accent)";
      if(!missing.includes(key)) missing.push(key);
    }
  });
  const banner = document.getElementById("legal-incomplete");
  if(!banner) return;
  if(missing.length){
    banner.style.display = "";
    banner.innerHTML = "<strong>Not ready to publish.</strong> Set <code>"
      + missing.join("</code>, <code>") + "</code> in <code>legal-details.js</code>. "
      + "Both this page and its sibling read from that one file.";
  } else {
    banner.style.display = "none";
  }
});

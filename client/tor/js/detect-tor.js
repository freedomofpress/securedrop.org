const TBB_UA_REGEX = /Mozilla\/5\.0 \(Windows NT 6\.1; rv:[0-9]{2}\.0\) Gecko\/20100101 Firefox\/([0-9]{2})\.0/;

function is_likely_tor_browser() {
  return window.navigator.userAgent.match(TBB_UA_REGEX) &&
         (window.navigator.mimeTypes &&
          window.navigator.mimeTypes.length === 0);
}

function tbb_version() {
  const ua_match = window.navigator.userAgent.match(TBB_UA_REGEX);
  const major_version = ua_match[1];
  return Number(major_version);
}

// Warn about using Javascript and not using Tor Browser
document.addEventListener("DOMContentLoaded", () => {
  const useTorBrowser = document.getElementById('js-use-tor-browser')

  if (is_likely_tor_browser()) {
    /* If the source is using Tor Browser, we want to encourage them to turn Tor
      Browser's Security Slider to "High", which enables various hardening
      methods, including disabling Javascript. Since JS is disabled by turning
      the Security Slider to "High", this code only runs if it set to another
      (less hardened) setting. */
    let torWarning = document.getElementById('js-tor-warning')
    torWarning.classList.remove('tor-warning--hidden')
    //  hides the warning to use tor, since users already have it
    useTorBrowser.classList.add('tor-warning--hidden')

    let torWarningClose = document.getElementById('js-tor-warning-close')
    torWarningClose.addEventListener('click', () => {
      torWarning.classList.add('tor-warning--hidden')
    })

  } else {
    // If the user is not using Tor Browser, we want to encourage them to do so.
    // TODO: Disable scrolling
    useTorBrowser.classList.remove('tor-warning--hidden')

    const closeUseTorBrowser = document.getElementById('js-use-tor-browser-close')
    closeUseTorBrowser.addEventListener('click', () => {
      useTorBrowser.classList.add('tor-warning--hidden')
    })
  }
});

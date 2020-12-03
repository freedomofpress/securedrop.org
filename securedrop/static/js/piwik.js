var idSite = 3;
var piwikTrackingApiUrl = 'https://analytics.freedom.press/piwik.php';

var _paq = window._paq = window._paq || [];

_paq.push(['setTrackerUrl', piwikTrackingApiUrl]);
_paq.push(['setSiteId', idSite]);
_paq.push(['trackPageView']);
_paq.push(['enableLinkTracking']);

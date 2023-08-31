// This user agent string matches Tor Browser 9 and 10 or Firefox Quantum (on desktop)
const TBB_UA_REGEX = /Mozilla\/5\.0 \((Windows NT 10\.0|X11; Linux x86_64|Macintosh; Intel Mac OS X 10\.[0-9]{2}|Windows NT 10\.0; Win64; x64|Android( [0-9]{2})?; Mobile); rv:[0-9]{2,3}\.0\) Gecko\/20100101 Firefox\/([0-9]{2,3})\.0/

// Use Tor css resource loading to check whether it's Tor Browser
const is_tor_resource_loaded = async () => new Promise(resolve => {
	setTimeout(() => resolve(false), 150)
	try {
		let css = document.createElement("link")
		css.href = "resource://torbutton-assets/aboutTor.css"
		css.type = "text/css"
		css.rel = "stylesheet"
		document.head.appendChild(css)
		css.onload = function() {
			resolve(true)
		}
		css.onerror = function() {
			resolve(false)
		}
		document.head.removeChild(css)
	} catch(e) {
		resolve(false)
	}
})

const is_likely_mobile_browser = function () {
	return window.navigator.userAgent.indexOf("Mobi") !== -1
}

const is_likely_tor_browser = async function () {
	return (
		// Tor Browser has the Tor/FF UA string
		window.navigator.userAgent.match(TBB_UA_REGEX) &&
		// Tor Browser always reports a GMT timezone
		new Date().getTimezoneOffset() == 0 &&
		// Tor Browser always reports device dimensions being the same
		// as window dimensions -- this is only true in a browser that
		// implements letterboxing, such as Firefox configured with
		// privacy.resistFingerprinting=true
		window.screen.width == window.innerWidth &&
		window.screen.height == window.innerHeight
	) || await is_tor_resource_loaded()
}

const is_likely_desktop_tor_browser = async function () {
	return !is_likely_mobile_browser() && await is_likely_tor_browser()
}


// Adjust <html> element classes according to tor detection
is_likely_tor_browser().then(result => {
	document.documentElement.classList.add(result ? 'tor' : 'no-tor')
})

// Warn about using Javascript and not using Tor Browser
document.addEventListener("DOMContentLoaded", async () => {
	if (sessionStorage.getItem('torWarningDismissed') === '1') {
		return
	}

	const useTorBrowser = document.getElementById('js-use-tor-browser')
	const instances = document.getElementById('js-instances')
	const body = document.body

	if (await is_likely_desktop_tor_browser()) {
		/* If the source is using Tor Browser in desktop, we want to encourage them to turn Tor
			Browser's Security Slider to "High", which enables various hardening
			methods, including disabling Javascript. Since JS is disabled by turning
			the Security Slider to "High", this code only runs if it set to another
			(less hardened) setting. */
		let torWarning = document.getElementById('js-tor-warning')
		torWarning.classList.remove('tor-warning--hidden')
		torWarning.setAttribute('aria-hidden', 'false')
		//  hides the warning to use tor, since users already have it
		useTorBrowser.classList.add('tor-warning--hidden')
		useTorBrowser.setAttribute('aria-hidden', 'true')
		// adds class to body that disables scrolling
		body.classList.add('no-scroll')
		// Tell instances and updates that there's a warning
		// so that homepage styles are adjusted
		if(instances) {
			instances.classList.add('instances--tor-warning')
		}

		const closeUseTorBrowser = document.getElementById('js-tor-warning-close')

		closeUseTorBrowser.addEventListener('click', () => {
			torWarning.classList.add('tor-warning--hidden')
			// hides warning for screen readers
			torWarning.setAttribute('aria-hidden', 'true')
			body.classList.remove('no-scroll')
			if(instances) {
				instances.classList.remove('instances--tor-warning')
			}
			sessionStorage.setItem('torWarningDismissed', '1')
		})
	} else if (is_likely_mobile_browser()) {
		let torWarning = document.getElementById('js-tor-mobile-warning')
		torWarning.classList.remove('tor-warning--hidden')
		torWarning.setAttribute('aria-hidden', 'false')
		//  hides the warning to use tor, since users already have it
		useTorBrowser.classList.add('tor-warning--hidden')
		useTorBrowser.setAttribute('aria-hidden', 'true')
		// adds class to body that disables scrolling
		body.classList.add('no-scroll')
		// Tell instances and updates that there's a warning
		// so that homepage styles are adjusted
		if(instances) {
			instances.classList.add('instances--tor-warning')
		}

		const closeUseTorBrowser = document.getElementById('js-tor-mobile-warning-close')

		closeUseTorBrowser.addEventListener('click', () => {
			torWarning.classList.add('tor-warning--hidden')
			// hides warning for screen readers
			torWarning.setAttribute('aria-hidden', 'true')
			body.classList.remove('no-scroll')
			if(instances) {
				instances.classList.remove('instances--tor-warning')
			}
			sessionStorage.setItem('torWarningDismissed', '1')
		})
	} else {
		// If the user is not using Tor Browser, we want to encourage them to do so.
		useTorBrowser.classList.remove('tor-warning--hidden')
		useTorBrowser.setAttribute('aria-hidden', 'false')
		body.classList.add('no-scroll')
		if(instances) {
			instances.classList.add('instances--tor-warning')
		}

		const closeUseTorBrowser = document.getElementById('js-use-tor-browser-close')
		closeUseTorBrowser.addEventListener('click', () => {
			useTorBrowser.classList.add('tor-warning--hidden')
			useTorBrowser.setAttribute('aria-hidden', 'true')
			body.classList.remove('no-scroll')
			if(instances) {
				instances.classList.remove('instances--tor-warning')
			}
			sessionStorage.setItem('torWarningDismissed', '1')
		})
	}
});

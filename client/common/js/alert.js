document.addEventListener('DOMContentLoaded', () => {
	const alert = document.getElementById('js-site-alert')

	try {
		const closeButton = document.getElementById('js-site-alert-button')
		// Users with Tor won't be able to use the button, so it will not be visible
		// if javaScript is disabled.
		closeButton.classList.remove('site-alert__close-button--hidden')

		closeButton.addEventListener('click', () => {
			alert.classList.add('site-alert--hidden')
			alert.setAttribute('aria-hidden', 'true')
		})
	} catch (e) {
		if (!(e instanceof TypeError)) {
			throw e
		}
	}
})

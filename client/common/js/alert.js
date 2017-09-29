document.addEventListener("DOMContentLoaded", () => {
	const alert = document.getElementById('js-site-alert')
	const mainNav = document.getElementById('js-main-nav')

	try{
		const closeButton = document.getElementById('js-site-alert-button')
		// Users with Tor won't be able to use the button, so it will not be visible
		// if javaScript is disabled.
		closeButton.classList.remove('site-alert__close-button--hidden')

		closeButton.addEventListener('click', () => {
			alert.classList.add('site-alert--hidden')
			mainNav.classList.remove('main-nav--alert')
		})
	} catch(e) {
		if(!(e instanceof TypeError)) {
			throw new Error(e)
		}
	}
})

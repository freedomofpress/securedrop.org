class SlidingNav {
	constructor(navEl, triggerEl, overlayEl) {
		this.active = false
		this.navEl = navEl
		this.triggerEl = triggerEl
		this.overlayEl = overlayEl
		this.toggleSlide = this.toggleSlide.bind(this)
		this.overlayEl.addEventListener('click', this.toggleSlide)
		this.triggerEl.addEventListener('click', this.toggleSlide)
	}

	toggleSlide(event) {
		event.preventDefault()
		this.active = !this.active
		this.render()
	}

	render() {
		const { navEl, triggerEl, overlayEl } = this
		if (this.active) {
			document.body.classList.add('no-scroll')
			navEl.classList.add('sliding-nav--is-active')
			triggerEl.classList.add('is-active')
			overlayEl.classList.add('shade--is-active')
			window.addEventListener('resize', this.toggleSlide)
		} else {
			document.body.classList.remove('no-scroll')
			navEl.classList.remove('sliding-nav--is-active')
			triggerEl.classList.remove('is-active')
			overlayEl.classList.remove('shade--is-active')
			window.removeEventListener('resize', this.toggleSlide)
		}
	}
}

document.addEventListener('DOMContentLoaded', () => {
	 // If js is running, adjust nav menus
	const navMenu = document.getElementById('js-nav-menu')
	const navButton = document.getElementById('js-nav-button')
	navMenu.classList.add('js-nav-menu-hidden')
	navMenu.setAttribute('aria-hidden', "true")
	navButton.classList.remove('js-nav-menu-hidden')
	navButton.setAttribute('aria-hidden', "false")
	// We're assuming there's only one sliding nav to be instantiated
	const navElement = document.getElementsByClassName('js-sliding-nav')[0]
	const triggerElement = navButton
	const overlayElement = document.getElementsByClassName('js-sliding-nav-overlay')[0]
	const slidingNav = new SlidingNav(navElement, triggerElement, overlayElement)
})

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
			navEl.classList.add('sliding-nav--is-active')
			triggerEl.classList.add('is-active')
			overlayEl.classList.add('shade--is-active')
		} else {
			navEl.classList.remove('sliding-nav--is-active')
			triggerEl.classList.remove('is-active')
			overlayEl.classList.remove('shade--is-active')
		}
	}
}

document.addEventListener('DOMContentLoaded', () => {
	// We're assuming there's only one sliding nav to be instantiated
	const navElement = document.getElementsByClassName('js-sliding-nav')[0]
	const triggerElement = document.getElementsByClassName('js-sliding-nav-trigger')[0]
	const overlayElement = document.getElementsByClassName('js-sliding-nav-overlay')[0]
	const slidingNav = new SlidingNav(navElement, triggerElement, overlayElement)
})

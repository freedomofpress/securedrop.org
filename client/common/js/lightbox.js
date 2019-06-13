import './lightbox.sass'

class Lightbox {
	constructor(link) {
		this._link = link

		this.open = this.open.bind(this)
		this.close = this.close.bind(this)
		this.createLightboxElements = this.createLightboxElements.bind(this)
		this.bindEscKey = this.bindEscKey.bind(this)
		this.unbindEscKey = this.unbindEscKey.bind(this)
		this.escListener = this.escListener.bind(this)

		this._link.addEventListener('click', this.open)
	}

	async createLightboxElements() {
		this.elements = {
			lightbox: document.createElement('div'),
			overlay: document.createElement('div'),
			container: document.createElement('div'),
			image: document.createElement('img'),
		}

		// Attributes
		this.elements.image.src = this._link.href
		this.elements.lightbox.classList.add('lightbox')
		this.elements.lightbox.setAttribute('hidden', true)
		this.elements.overlay.classList.add('lightbox__overlay')
		this.elements.image.classList.add('lightbox__image')
		this.elements.container.classList.add('lightbox__container')

		// DOM Tree
		document.body.appendChild(this.elements.lightbox)
		this.elements.lightbox.appendChild(this.elements.overlay)
		this.elements.lightbox.appendChild(this.elements.container)
		this.elements.container.appendChild(this.elements.image)

		// Events -- clicking anywhere should close the lightbox
		this.elements.overlay.addEventListener('click', this.close)
		this.elements.container.addEventListener('click', this.close)

		await new Promise((resolve, reject) => {
			this.elements.image.onload = resolve
			setTimeout(3000, reject)
		})

		return this.elements.image
	}

	async open(e) {
		e.preventDefault()
		e.stopPropagation()

		this.bindEscKey()

		// If this is the first open, make sure to create the necessary elements
		if (!('elements' in this)) {
			this._link.classList.add('lightbox-link--loading')
			await this.createLightboxElements()
			this._link.classList.remove('lightbox-link--loading')
		}

		this.elements.lightbox.setAttribute('hidden', false)
		this.elements.lightbox.classList.add('lightbox--visible')

		// Reposition the image container
		this.elements.container.style.top = window.scrollY + 'px'
	}

	close(e) {
		this.elements.lightbox.setAttribute('hidden', true)
		this.elements.lightbox.classList.remove('lightbox--visible')
		this.unbindEscKey()
		e.preventDefault()
		e.stopPropagation()
	}

	escListener(e) {
		if (e.keyCode === 27) this.close(e)
	}

	bindEscKey() {
		document.addEventListener('keyup', this.escListener)
	}

	unbindEscKey() {
		document.removeEventListener('keyup', this.escListener)
	}
}


// Autodetect API
document.addEventListener('DOMContentLoaded', () => {
	const lightboxLinks = Array.from(document.querySelectorAll('.js-lightbox'))
	lightboxLinks.forEach(link => new Lightbox(link))
})

import './lightbox.sass'

class Lightbox {
	constructor(link) {
		this._link = link
		this._caption = link.dataset.lightboxCaption
		this._currentlyOpening = false

		this.options = {
			lightboxPadding: 10, // must match value from CSS on the container
			lightboxMargin: 20,
		}

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
			container: document.createElement('figure'),
			image: document.createElement('img'),
			caption: null,
		}

		if (this._caption) {
			this.elements.caption = document.createElement('figcaption')
		}

		// Attributes
		this.elements.image.src = this._link.href
		this.elements.lightbox.classList.add('lightbox')
		this.elements.lightbox.setAttribute('hidden', true)
		this.elements.lightbox.setAttribute('aria-hidden', true)
		this.elements.lightbox.setAttribute('role', 'dialog')
		this.elements.overlay.classList.add('lightbox__overlay')
		this.elements.overlay.setAttribute('aria-hidden', true)
		this.elements.image.classList.add('lightbox__image')
		this.elements.container.classList.add('lightbox__container')
		if (this.elements.caption) {
			this.elements.caption.classList.add('lightbox__caption')
		}

		// DOM Tree
		document.body.appendChild(this.elements.lightbox)
		this.elements.lightbox.appendChild(this.elements.overlay)
		this.elements.lightbox.appendChild(this.elements.container)
		if (this.elements.caption) {
			this.elements.caption.innerHTML = this._caption
			this.elements.container.appendChild(this.elements.caption)
		}
		this.elements.container.appendChild(this.elements.image)

		// Events -- clicking anywhere should close the lightbox
		this.elements.overlay.addEventListener('click', this.close)
		this.elements.container.addEventListener('click', this.close)

		await new Promise((resolve, reject) => {
			this.elements.image.onload = resolve
		})

		return this.elements.image
	}

	async open(e) {
		e.preventDefault()
		e.stopPropagation()

		// Prevent double-clicking errors
		if (this._currentlyOpening) return

		this.bindEscKey()

		this._currentlyOpening = true

		// If this is the first open, make sure to create the necessary elements
		if (!('elements' in this)) {
			this._link.classList.add('lightbox-link--loading')
			await this.createLightboxElements()
			this._link.classList.remove('lightbox-link--loading')
		}

		this.elements.lightbox.setAttribute('hidden', false)
		this.elements.lightbox.setAttribute('aria-hidden', false)
		this.elements.lightbox.classList.add('lightbox--visible')

		/* Reposition and resize the image container
		 * There's a lot of math here but it basically works like this:
		 *
		 * 1. The maximum image height is either the natural image height or the height of the screen,
		 *    whichever is smaller
		 * 2. The *actual* image width is either the width that is the correct aspect ratio for the
		 *    height chosen in step one, the image's natural width, or the width of the screen,
		 *    whichever is smallest
		 * 3. The *actual* image height therefore is whatever matches the aspect ratio of the image
		 *    width selected in step two
		 *
		 * Note that we only use the calculated width in the style and allow the browser to use the
		 * natural aspect ratio of the image to automatically determine the height. We use the
		 * calculated image height to center the image.
		 */
		const imageAspectRatio = this.elements.image.height / this.elements.image.width
		const imageMaxHeight = Math.min(
			this.elements.image.naturalHeight,
			// Leave 140px for caption
			window.innerHeight - 140 - this.options.lightboxPadding * 2 - this.options.lightboxMargin * 2
		)
		const imageWidth = Math.min(
			this.elements.image.naturalWidth,
			imageMaxHeight / imageAspectRatio,
			window.innerWidth - this.options.lightboxPadding * 2 - this.options.lightboxMargin * 2
		)
		const imageHeight = imageWidth * imageAspectRatio
		this.elements.container.style.width = imageWidth + 'px'
		// Center
		this.elements.container.style.top = ((
			window.innerHeight
			- imageHeight
			- 140 // Leave 140px for caption
		) / 2 + window.scrollY) + 'px'
		this.elements.container.style.left = ((
			window.innerWidth
			- imageWidth
		) / 2) + 'px'

		this._currentlyOpening = false
	}

	close(e) {
		this.elements.lightbox.setAttribute('hidden', true)
		this.elements.lightbox.setAttribute('aria-hidden', true)
		this.elements.lightbox.classList.remove('lightbox--visible')
		this.elements.container.style.removeProperty('width')
		this.elements.container.style.removeProperty('top')
		this.elements.container.style.removeProperty('left')
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

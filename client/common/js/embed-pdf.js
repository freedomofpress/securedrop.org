import PDFObject from 'pdfobject';

function embedPdf(el) {
	var options = {
		fallbackLink: `<a class="pdfobject-fallback" href="[url]">
<svg class="pdfobject-fallback__icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
    <path d="M0 0v8h7v-4h-4v-4h-3zm4 0v3h3l-3-3z" fill="white"></path>
</svg>
		<span>Download <strong>${el.dataset.fileTitle}</strong></span></a>`,
	}
	PDFObject.embed(el.dataset.fileUri, el, options)
}

document.addEventListener('DOMContentLoaded', () => {
	const inlinePdfs = Array.from(document.querySelectorAll('.js-pdf'))
	inlinePdfs.forEach(embedPdf)
})

import PDFObject from 'pdfobject';

function embedPdf(el) {
	var options = {
		fallbackLink: `<a class="pdfobject-fallback" href="[url]">
        <img class="pdfobject-fallback__icon" src="${el.dataset.iconUri}" alt="Document Icon">
		<span>Download <strong>${el.dataset.fileTitle}</strong></span></a>`,
	}
	PDFObject.embed(el.dataset.fileUri, el, options)
}

document.addEventListener('DOMContentLoaded', () => {
	const inlinePdfs = Array.from(document.querySelectorAll('.js-pdf'))
	inlinePdfs.forEach(embedPdf)
})

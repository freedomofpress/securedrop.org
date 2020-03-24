import PDFObject from 'pdfobject';

function embedPdf(el) {
	var options = {
		fallbackLink: '<p class="pdfobject-fallback"><strong>PDF Not Displayed</strong>: This browser does not support inline PDFs. Please download the PDF to view it: <a href="[url]">Download PDF</a>.</p>'
	}
	PDFObject.embed(el.dataset.fileUri, el, options)
}

document.addEventListener('DOMContentLoaded', () => {
	const inlinePdfs = Array.from(document.querySelectorAll('.js-pdf'))
	inlinePdfs.forEach(embedPdf)
})

import {jsPDF} from 'jspdf';

function saveaspdf(divId, title) {
    console.log('thanks');
    var doc = new jsPDF();
    doc.fromHTML(`<html><head><title>${title}</title></head><body>` + document.getElementById(divId).innerHTML + `</body></html>`);
    doc.save('insights.pdf');
}

export default saveaspdf;
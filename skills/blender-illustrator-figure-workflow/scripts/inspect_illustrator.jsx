#target illustrator
// Read-only document inspection. Writes only the chosen text report.
(function () {
    if (!app.documents.length) throw Error('Open the intended Illustrator document first.');
    var lines = [], docs = [];
    for (var i = 0; i < app.documents.length; i++) {
        var d = app.documents[i], path = '(unsaved document)';
        try { path = d.fullName.fsName; } catch (e) {}
        docs.push((i + 1) + ': ' + path);
    }
    var answer = prompt('Choose the document number:\n' + docs.join('\n'), '1');
    if (answer === null) return;
    var index = Number(answer) - 1;
    if (index < 0 || index >= app.documents.length || index !== Math.floor(index)) throw Error('Invalid document number');
    var doc = app.documents[index];
    var out = File.saveDialog('Save inspection report', '*.txt');
    if (!out) return;
    if (!/\.txt$/i.test(out.name)) throw Error('Report must end with .txt');
    if (out.exists) throw Error('Choose a new report filename; overwrite refused.');
    function safe(s) { return String(s).replace(/[\r\n\t]/g, ' '); }
    function walk(p, address) {
        var row = [address, p.typename, safe(p.name), p.geometricBounds.toString(),
                   'hidden=' + p.hidden, 'locked=' + p.locked, 'opacity=' + p.opacity];
        try { row.push('uuid=' + p.uuid); } catch (e) {}
        if (p.typename === 'TextFrame') row.push('text=' + safe(p.contents));
        if (p.typename === 'PathItem') row.push('clipping=' + p.clipping);
        if (p.typename === 'RasterItem' || p.typename === 'PlacedItem') {
            try { var m = p.matrix; row.push('matrix=' + [m.mValueA,m.mValueB,m.mValueC,m.mValueD,m.mValueTX,m.mValueTY]); } catch (e) {}
        }
        lines.push(row.join('\t'));
        if (p.typename === 'GroupItem') for (var j = 0; j < p.pageItems.length; j++)
            if (p.pageItems[j].parent === p) walk(p.pageItems[j], address + '/' + j);
    }
    function visitLayer(l, address) {
        lines.push('LAYER\t' + address + '\t' + safe(l.name) + '\tvisible=' + l.visible + '\tlocked=' + l.locked);
        for (var j = 0; j < l.pageItems.length; j++) if (l.pageItems[j].parent === l) walk(l.pageItems[j], address + ':' + j);
        for (var j = 0; j < l.layers.length; j++) visitLayer(l.layers[j], address + '.' + j);
    }
    lines.push('DOCUMENT\t' + docs[index] + '\tsaved=' + doc.saved);
    for (var i = 0; i < doc.artboards.length; i++) lines.push('ARTBOARD\t' + i + '\t' + doc.artboards[i].artboardRect);
    for (var i = 0; i < doc.layers.length; i++) visitLayer(doc.layers[i], String(i));
    out.encoding = 'UTF-8';
    if (!out.open('w')) throw Error('Cannot open report for writing');
    try { out.write(lines.join('\n')); } finally { out.close(); }
    alert('Inspection complete. Document not modified.\n' + out.fsName);
})();

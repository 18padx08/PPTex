// TeXworksScript
// Title: Toggle Table (PPTex)
// Shortcut: Ctrl+Shift+T
// Description: Encloses the current selection in \emph{}
// Author: Patrick Amrein (code taken from Jonathan Kew)
// Version: 0.3
// Date: 2010-01-09
// Script-Type: standalone
// Context: TeXDocument

function addOrRemove(prefix, suffix) {
    var txt = TW.target.selection;
    var len = txt.length;
    var rows = txt.split(";");
    var arrTxt = [];
    for (row in rows) {
        arrTxt.push("[" + rows[row] + "]");
    }
    txt = arrTxt.join();
   
    var wrapped = prefix + txt + suffix;
    var pos = TW.target.selectionStart;
    if (pos >= prefix.length) {
        TW.target.selectRange(pos - prefix.length, wrapped.length);
        if (TW.target.selection == wrapped) {
            TW.target.insertText(txt);
            TW.target.selectRange(pos - prefix.length, len);
            return;
        }
        TW.target.selectRange(pos, len);
    }
    TW.target.insertText(wrapped);
    TW.target.selectRange(pos + prefix.length, len);
    return;
};

addOrRemove("{%table {'xheader':[], 'yheader':[], 'extended':True, 'desc': '', 'xdata':[", "]}%}");
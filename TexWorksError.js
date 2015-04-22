// TeXworksScript
// Title: Toggle Error (PPTex)
// Shortcut: Ctrl+Alt+E
// Description: constructs the error syntax
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
    var tmpText = '';
    var i = 0;
    for (row in rows) {
        //we have function, fname, digits; symbols
        //where symbols is splitted with &
        
        var split = null;
        if(i == 0) {
            split = rows[row].split(',');
            tmpText = "'function': '" + split[0] + "', 'fname':'" + split[1] + "', 'errors':True, 'digits':" + split[2] + "";
        }
        else {
            split = rows[row].split('&');
            tmpText += ",'symbols':[";
            var counter = 0;
            for (sp in split) {
                var tt = "";
                symbolargs = split[sp].split(',');
                tmpText += "{'sym':'" + symbolargs[0] + "', 'val':" + symbolargs[1] + (symbolargs.length > 2? ",'indep':True, 'uncert':" + symbolargs[2] + "}":"}");
                if (counter < split.length - 1) tmpText += ",";
                counter++;
            }
            tmpText += "]";
        }
       // arrTxt.push(split);
        i++;
    }
    txt = tmpText;

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

addOrRemove("{%evaltex {", "}%}");
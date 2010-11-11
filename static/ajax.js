
function isInt(x) {
    var y = parseInt(x, 10);
    if (isNaN(y)) {
        return false;
    } 
    return x === y && x.toString() === y.toString(); 
}
 
function ProcessData(xmlhttp, board, poll) {
    var str = xmlhttp.responseText;
    JSON.parse(str, function (key, data) {
        if (key === "reveal") {
            while (data !== "") {
                var x = parseInt(data[0], 10);
                var y = parseInt(data[1], 10);
                var p = data[2];
                var adj = parseInt(data[3], 10);
                var t = board.getTile(x, y);
                t.adjacency = adj;
                t.player = p;
                data = data.substr(4);

            }
        }        
    });
    
    if (poll) {
        poll(board);
    }
    
    return true;
}

function Poll(board) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState === 4 && xmlhttp.status === 200) {
            ProcessData(xmlhttp, board, Poll);
        }
    };
    xmlhttp.open("GET", "?action=poll", true);
    xmlhttp.send();
}

function Refresh(board) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState === 4 && xmlhttp.status === 200) {
            ProcessData(xmlhttp, board, Poll);
        }
    };
    xmlhttp.open("GET", "?action=refresh", true);
    xmlhttp.send();    
}

function SendClick(x, y, board) {
    var xmlhttp = new XMLHttpRequest();
    if (!isInt(x) || !isInt(y)) {
        throw "Click coordinates must be integers.";
    }
    
    xmlhttp.open("GET", "?action=click&x=" + x + "&y=" + y, true);
    xmlhttp.send();
}

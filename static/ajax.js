
function isInt(x) {
    var y = parseInt(x, 10);
    if (isNaN(y)) {
        return false;
    } 
    return x === y && x.toString() === y.toString(); 
}

Net = new function() {

    /*
     * Process received data. Call poll(game) when this is done.
     */
    var ProcessData = function (xmlhttp, game, poll) {
        var str = xmlhttp.responseText;
        var obj = JSON.parse(str);
        var data;
        if (obj.reveal)
        {
            data = obj.reveal;
            var t;

            for (t in data){
                var x = parseInt(data[t].x,10);
                var y = parseInt(data[t].y,10);
                var p = data[t].pl;
                var adj = data[t].val;
                var flag = data[t].fl
                var tile = game.getTile(x, y);

                //alert(x+","+y);
                tile.adjacency = adj;
                tile.player = p;
                tile.flag = flag;
                tile.onModify();
            }

            //Render is defined in game.html.
            game.RenderGame();
        }
        if (obj.players)
        {
            data = obj.players;
            var p;
            var plist = new Array();

            for (p in data) {
                var po = {};
                po.name = data[p].name;
                po.present = data[p].present;
                po.index = data[p].id;
                plist.push(po);
            }
            game.players = plist;
            game.RenderPlayers();
        }
        if (obj.flag)
        {
            var x,y,flag,tile;
            x = obj.flag.x
            y = obj.flag.y
            flag = obj.flag.fl
            tile = game.getTile(x,y);
            tile.flag = flag;
            tile.onModify();
            
            game.RenderGame();
        }
        if (poll) {
            poll(game);
        }

        return true;
    }

    var SendRequest = function (game, method, string, reply, poll) {
        var xmlhttp = new XMLHttpRequest();
        if (reply){
            xmlhttp.onreadystatechange = function () {
                if (xmlhttp.readyState === 4 && xmlhttp.status === 200) {
                    if (poll) {
                        ProcessData(xmlhttp, game, Net.Poll);
                    }
                    else {
                        ProcessData(xmlhttp, game, null);
                    }
                }
                /*
                else if (xmlhttp.status === 404) {
                    //The game no longer exists
                    alert("The game has timed out.");
                }
                */
            };
        }
        xmlhttp.open(method, string, true);
        xmlhttp.send();
    }

    /*
     * Send a poll request.
     */
    this.Poll = function(game) {
        SendRequest(game,"GET", "?action=poll", true, true);
    }

    /*
     * Send a refresh request.
     */
    this.Refresh = function(game) {
        SendRequest(game,"GET", "?action=refresh",true, true);
    }

    /*
     * Send a click message.
     */
    this.SendClick = function (x, y, flag) {
        if (!isInt(x) || !isInt(y)) {
            throw "Click coordinates must be integers.";
        }
        if (flag) {
            SendRequest(null,"GET","?action=flag&x=" + x + "&y=" + y,false,false);
        }
        else {
            SendRequest(null,"GET","?action=click&x=" + x + "&y=" + y,false,false);
        }
    }

    this.sendLeave = function () {
        alert("leaving!")
        SendRequest(null,"GET","?action=leave",false,false)
    }
};

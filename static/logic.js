
function Tile() {
    this.player = 0;
    this.adjacency = 0;
    this.flag = 0;
    
    //An alternative to renderGameFunc!
    this.onModify = function () {};
}

/*
 * Game namespace/object. Keeps a representation of all of the game data.
 */
Game = new function() {

    this.Init = function(w, h) {
        var i;
        this.width = w;
        this.height = h;
        this.data = new Array(w * h);
        this.players = {};

        //Set these callbacks to draw the game.
        this.renderGameFunc = function () {};
        this.renderPlayersFunc = function() {};
        this.onWin = function () {};

        for (i = 0; i < w * h; i = i + 1) {
            this.data[i] = new Tile();
        }
    }

    this.getTile = function (x, y) {
        if (x < 0 || x >= this.width || y < 0 || y >= this.height) {
            throw "Coordinate out of bounds.";
        }
        return this.data[x + y * this.width];
    };

    /*
     * iterateTiles( function (x, y, tile) );
     * Iterates over every tile, calling this function once for each one.
     */
    this.iterateTiles = function (callback) {
        var xx;
        var yy;
        for (xx = 0; xx < this.width; xx = xx +  1) {
            for (yy = 0; yy < this.height; yy = yy + 1) {
                callback(xx, yy, this.data[xx + yy * this.width]);
            }
        }
    };

    this.RenderGame = function () {
        this.renderGameFunc();
    }
    this.RenderPlayers = function() {
        this.renderPlayersFunc();
    }
};

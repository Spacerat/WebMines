
function Tile(){
    this.player=0;
    this.adjacency=0;
}

function Board(w, h) {
    this.width = w
    this.height = h
    this.data = new Array(w*h);
    this.canvas = null;
    var _n;
    for (_n=0;_n<w*h;_n=_n+1) {
        this.data[_n]=new Tile();
    }

    this.getTile = function(x,y)
    {
        if (x<0 || x>=this.width || y<0 || y>=this.height) {
            throw "Coordinate out of bounds.";
        }
        return this.data[x+y*this.width];
    }
    
    this.iterateTiles = function(callback) {
        var xx;
        var yy;
        for (xx = 0;xx<this.width;xx=xx+1) {
            for (yy = 0;yy<this.height;yy=yy+1) {
                callback(xx,yy,this.data[xx+yy*this.width])
            }
        }
    }
    
    this.renderToCanvas = function(canvas) {
        if (canvas==null) {
            canvas = this.canvas;
        }
        this.canvas = canvas;
        canvas.width = canvas.width
        var c = canvas.getContext('2d');
        var w = canvas.width;
        var h = canvas.height;
        c.strokeStyle ='#000';
        c.lineWidth = 1;
        c.textAlign = 'center';
        var tw = w/this.width;
        var th = h/this.height;
        this.iterateTiles(function(x,y,tile){
            
                c.strokeRect(x*tw,y*th,w,h);
            if (tile.player>0){
                c.strokeText(tile.adjacency,x*tw+(tw/2),y*th+(th/2))
            }
        })    
    }

    return true;
}
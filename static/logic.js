
function Board(w, h) {
    this.width = w
    this.height = h
    this.data = new Array(w*h);
    var _n;
    for (_n=0;_n<w*h;_n=_n+1) {
        this.data[_n]=0
    }

    this.getTile = function(x,y)
    {
        if (x<0 || x>=this.width || y<0 || y>=this.height) {
            throw "Coordinate out of bounds.";
        }
        return this.data[x+y*this.height];
    }

    this.setTile = function(x,y,value) {
        if (x<0 || x>=this.width || y<0 || y>=this.height) {
            throw "Coordinate out of bounds.";
        }
        this.data[x+y*this.height] = value;
    }

    this.iterateTiles = function(callback) {
        var xx;
        var yy;
        for (xx = 0;xx<this.width;xx=xx+1) {
            for (yy = 0;yy<this.width;yy=yy+1) {
                callback(xx,yy,this.data[xx+yy*this.height])
            }
        }
    }
    
    this.renderToCanvas = function(canvas) {
        canvas.width = canvas.width
        var c = canvas.getContext('2d');
        var w = canvas.width;
        var h = canvas.height;
        c.strokeStyle ='#000';
        c.lineWidth = 1;
        c.textAlign = 'center';
        var tw = w/this.width;
        var th = h/this.height;
        this.iterateTiles(function(x,y,value){
            c.strokeRect(x*tw,y*th,w,h);
            c.strokeText(value,x*tw+(tw/2),y*th+(th/2))
        })    
    }

    return true;
}
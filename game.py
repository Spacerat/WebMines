
from random import randint, choice
import string

#In order of increasing wordyness
class BoardError(Exception): pass
class BoardTooSmallError(BoardError): pass
class BoardTooManyBombsError(BoardError): pass
class BoardCoordOutOfRangeExcepton(BoardError): pass

class GameError(Exception): pass
class GameNameTakenError(GameError): pass
class GameInvalidPlayer(GameError, TypeError): pass

def GenID(length=8):
    idchars = string.letters + string.digits
    id=''
    for x in range(8):
        id+=choice(idchars)  
    return id

class Player():
    
    players={}
    
    def __init__(self,name):
        self.name = name
        self.id=''
        while (self.id=='' or self.id in Player.players):
            self.id = GenID()
        self.games = []
        Player.players[self.id] = self
    
    #Add a game to this player's list of current games
    def add_game(self,game):
        self.games.append(game)
        
    #Remove a game from this player's list of current games.
    #Remove the player if this removes the last game.
    def remove_game(self,game):
        self.games.remove(game)
        if len(self.games)==0:
            self.disconnect()
    
    def disconnect(self):
        del Player.players[self.id]

class Game():
    
    games={}
    
    def __init__(self,name,width=10,height=10,mines=-1,wrap=False):
        for g in Game.games.values():
            if g.name == name:
                raise GameNameTakenError, "Game name already taken."
        
        self.started = False
        self.name = name
        self.board = Board(width,height,mines,wrap)
        #generate random id
        id = ''
        while (id=='' or id in Game.games):
            id=GenID()

        self.id = id
        Game.games[id] = self
        self.players=[]
        
    @property
    def width(self): return self.game.width
    @property
    def height(self): return self.game.height
        
    def add_player(self,player):
        if isinstance(player,Player):
            p = player
        elif isinstance(player,basestring):
            p = Player(str(player))
        else:
            raise GameInvalidPlayer, "Expecting Player or basestring, got "+str(type(player))
        
        self.players.append(p)
        return
        
    def close(self):
        for p in self.players:
            p.remove_game(self)
        del Game.games[self.id]
        
class Tile:
    def __init__(self,pos,is_bomb=False):
        self.bomb = is_bomb
        self.uncovered = 0
        self.adjacency = 0
        self.flag = 0
        self.pos = pos
        self._checked = False
    
    def __str__(self):
        if self.bomb: return "X|"+str(self.uncovered)
        return str(self.adjacency) + "|" + str(self.uncovered)
        
class Board:
    def __init__(self,width,height,bombs=-1,wrap=False):
        if width<4 or height<4:
            raise BoardTooSmallError, "The game board (%dx%d) must be larger than 3x3."%(width,height)
        
        #Set settings
        self.width=width
        self.height=height
        self.bombs=bombs
        self.wrap=wrap
        if bombs==-1: self.bombs =  int(((width*height)-9)/7)
        if width*height-14<self.bombs:
            raise BoardTooManyBombsError, "%d bombs is too many. The largest allowed number of bombs is width*height-14 = %d"%(self.bombs,width*height-14)
        
        #Initialise array
        self.tiles=[[Tile((col,row)) for col in range(height)] for row in range(width)]
        
        #Add random bombs
        b = self.bombs
        while b>0:
            x = randint(0,width-1)
            y = randint(0,height-1)
            if self.set_bomb(x,y): b-=1
            
    #Check if the given coordinates point to a valid tile.
    def validate_coords(self,x,y):
        if self.wrap:
            return True
        if x<0 or x>=self.width: return False
        if y<0 or y>=self.height: return False
        return True
    
    #Get the tile instance at the given coordinate.
    def get_tile(self,x,y):

        if self.wrap:
            x=x%self.width
            y=y%self.height
            return self.tiles[x][y]
        else:
            
            if not self.validate_coords(x,y): return None
            return self.tiles[x][y]
        
    #Get a list of tiles adjacent to the tile at the given coordinate.
    def get_adjacent_tiles(self,x,y):
        ret = []
        for xx in range(x-1,x+2):
            for yy in range(y-1,y+2):
                if xx==x and yy==y: continue
                t = self.get_tile(xx,yy)
                if t: ret.append(t)
        return ret
    
    #Give a tile bomb status
    def set_bomb(self,x,y):
        if self.is_bomb(x,y): return False
        t = self.get_tile(x,y)
        if t==None:
            raise BoardCoordOutOfRangeError, "Tile coordinate (%d,%d) out of bounds"%(x,y)
        t.bomb = True
        for x in self.get_adjacent_tiles(x,y):
            x.adjacency+=1
        return True
    
    #Check if there is a bomb at the given coordinate
    def is_bomb(self,x,y):
        t = self.get_tile(x,y)
        if not t: return False
        return t.bomb

    
    #Return a list of revealed tiles
    def reveal(self,player,x,y):
        ret = self._recurse_reveal(player, x, y)
        for l in self.tiles:
            for t in l:
                t._checked = False
        return ret
                
    def _recurse_reveal(self,player,x,y):
        
        t = self.get_tile(x,y)
        if not t: return
        if t._checked: return
        t._checked = True
        
        if t.uncovered == 0:  
            t.uncovered = player
            ret = [t]
            if t.adjacency==0:
                #For some reason, get_adjacent_tiles was breaking this.
                for xx in range(x-1,x+2):
                    for yy in range(y-1,y+2):
                        con = self._recurse_reveal(player,xx,yy)
                        if con: ret += con
                        
            t._checked=1
            return ret
        
    
    def __str__(self):
        s=""
        for x in self.tiles:
            for y in x:
                s+="%s "%str(y).center(3)
            s+="\n"
        return s


if __name__ == "__main__":
    b = Board(10,10)
    print b
    print ""
    print [t.pos for t in b.reveal(1,0,0)]
    print ""
    print b

    
    

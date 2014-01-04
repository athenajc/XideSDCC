import wx

from ide_global import *

if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Monaco',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 12,
              'size2': 10,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Courier 10 Pitch',
              'helv' : 'Ubuntu Mono',
              'other': 'new century schoolbook',
              'size' : 11,
              'size2': 10,
             }

def wxT(s):
    return s

def init_default_style(self):    
    self.SetBufferedDraw(True)
    self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
    self.StyleClearAll()  # Reset all to be like the default

    # Global default styles for all languages
    self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(mono)s,size:%(size2)d" % faces)
    self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
    self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
    self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

    # Indentation and tab stuff
    self.SetUseTabs(False)
    self.SetTabIndents(True)
    self.SetTabWidth(4)
    self.SetIndent(4)
    self.SetIndentationGuides(True)
    self.SetBackSpaceUnIndents(True)    
    
    #-- set margin for line number display
    self.SetMarginType(0, stc.STC_MARGIN_NUMBER)
    self.SetMarginWidth(0, 48)

    self.SetMarginWidth(1, 16) # marker margin
    self.SetMarginType(1, stc.STC_MARGIN_SYMBOL)
    self.SetMarginSensitive(1, True)

    #-- set margin for fold margin
    self.SetMarginWidth(2, 16) # fold margin
    self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
    self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
    self.SetMarginSensitive(2, True)

    self.SetFoldFlags(stc.STC_FOLDFLAG_LINEBEFORE_CONTRACTED | stc.STC_FOLDFLAG_LINEAFTER_CONTRACTED)

    self.SetProperty("fold", "1")
    self.SetProperty("fold.compact", "1")
    self.SetProperty("fold.comment", "1")

    grey = wx.Colour(128, 128, 128)
    self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_BOXMINUS, wx.WHITE, grey)
    self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_BOXPLUS,  wx.WHITE, grey)
    self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,    wx.WHITE, grey)
    self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNER,  wx.WHITE, grey)
    self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_BOXPLUSCONNECTED,  wx.WHITE, grey)
    self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, wx.WHITE, grey)
    self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,  wx.WHITE, grey)

    self.MarkerDefine(MARKNUM_BREAK_POINT,  stc.STC_MARK_CIRCLE, wx.BLACK, wx.GREEN)
    self.MarkerDefine(MARKNUM_CURRENT_LINE, stc.STC_MARK_ARROW, wx.BLUE, grey)

    del grey
#---------------------------------------------------------------------------------------------------
class DocColors():
    def __init__(self):
        self.default =      wx.Colour(10,0,10)

        self.comment =      wx.Colour(128,128,155)
        self.commentblock = wx.Colour(128,128,255)
        self.commentline =  wx.Colour(143, 43, 10)
        self.commentdoc   = wx.Colour(128,128,255)

        self.identifier =   wx.Colour(60,60,60)

        self.character =    wx.Colour(225,128,0)
        self.number =       wx.Colour(0,196,0)
        self.operator =     wx.Colour(128,64,164)
        self.string =       wx.Colour(225,127,0)
        self.stringeol =    wx.Colour(225,0,0)

        self.word =         wx.Colour(0,0,147)
        self.word1 =        wx.Colour(127,0,247)
        self.word2 =        wx.Colour(0,0,127)
        self.word3 =        wx.Colour(0,128,255)
        self.word4 =        wx.Colour(196,196,0)

        self.classname =    wx.Colour(0,128,0)
        self.defname =      wx.Colour(0,0,128)
        self.triple =       wx.Colour(0,0,0)
        self.tripledouble = wx.Colour(0,0,0)

        self.preprocessor = wx.Colour(0,128,60)

color = DocColors()

def default_lexer(self):
    style = [
        #stc.STC_LUA_CHARACTER = [7, color.character],
        #stc.STC_LUA_COMMENT = [1, color.COMMENT, "Italic"],
        #stc.STC_LUA_COMMENTDOC = [3, color.COMMENTBLOCK, "Italic"],
        #stc.STC_LUA_COMMENTLINE = [2, color.COMMENT, "Italic"],
        #stc.STC_LUA_DEFAULT = [0, color.DEFAULT],
        #stc.STC_LUA_IDENTIFIER = [11, color.identifier],
        #stc.STC_LUA_LITERALSTRING = [8, color.STRING],
        #stc.STC_LUA_NUMBER = [4, color.number],
        #stc.STC_LUA_OPERATOR = [10, color.operator, "Bold"],
        #stc.STC_LUA_PREPROCESSOR = [9, color.PREPROCESSOR],
        #stc.STC_LUA_STRING = [6, color.STRING],
        #stc.STC_LUA_STRINGEOL = [12, color.STRINGEOL],
        #stc.STC_LUA_WORD = [5, color.WORD, "Bold"],
        #stc.STC_LUA_WORD2 = [13, color.WORD2],
        #stc.STC_LUA_WORD3 = [14, color.WORD3],
        #stc.STC_LUA_WORD4 = [15, color.WORD4],
        #stc.STC_LUA_WORD5 = [16, color.WORD4],
        #stc.STC_LUA_WORD6 = [17, color.WORD4],
    ]
    for v in style:
        self.StyleSetForeground(v[0], v[1])

    #keyword = [[break case catch continue debugger default delete
                      #do else finally for def if in instanceof new
                      #return switch this throw try typeof var void while
                      #wit def ]]

    #--Key words
    #self.SetKeyWords(0, wxT(keyword))
    #self.SetKeyWords(1, wxT("void int short char long double float #include #define #typedef"))
    #self.SetKeyWords(2, wxT("__init__ self parent __main__"))
    #self.SetKeyWords(3, wxT("NULL TRUE FALSE None true False"))

#-------------------------------------------------------------------
def python_lexer(self):
    self.SetLexer(stc.STC_LEX_PYTHON)
    #self.SetKeyWords(0, " ".join(keyword.kwlist))

    self.SetProperty("fold", "1")
    self.SetProperty("tab.timmy.whinge.level", "1")
    self.SetViewWhiteSpace(False)

    # Global default styles for all languages
    self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
    self.StyleClearAll()  # Reset all to be like the default

    # Global default styles for all languages
    self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(mono)s,size:%(size2)d" % faces)
    self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
    self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
    self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

    # Python styles
    self.StyleSetSpec(stc.STC_P_DEFAULT,     "fore:#000000,face:%(mono)s,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_NUMBER,      "fore:#007F7F,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_STRING,      "fore:#7F007F,face:%(mono)s,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_CHARACTER,   "fore:#7F007F,face:%(mono)s,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_WORD,        "fore:#00007F,bold,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_TRIPLE,      "fore:#7F0000,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE,"fore:#7F0000,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_CLASSNAME,   "fore:#0000FF,bold,underline,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_DEFNAME,     "fore:#007F7F,bold,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_OPERATOR,    "bold,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_IDENTIFIER,  "fore:#000000,face:%(mono)s,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_COMMENTBLOCK,"fore:#7F7F7F,size:%(size)d" % faces)
    self.StyleSetSpec(stc.STC_P_STRINGEOL,   "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)

    self.SetCaretForeground("BLUE")

    #style = [
        #[stc.STC_P_CHARACTER,    color.character],
        #[stc.STC_P_CLASSNAME,    color.CLASSNAME],
        #[stc.STC_P_COMMENTBLOCK, color.COMMENTBLOCK],
        #[stc.STC_P_COMMENTLINE,  color.commentline],
        #[stc.STC_P_DEFAULT,      color.DEFAULT],
        #[stc.STC_P_DEFNAME,      color.DEFNAME],
        #[stc.STC_P_IDENTIFIER,   color.identifier],
        #[stc.STC_P_NUMBER,       color.number],
        #[stc.STC_P_OPERATOR,     color.operator],
        #[stc.STC_P_STRING,       color.STRING],
        #[stc.STC_P_STRINGEOL,    color.STRINGEOL],
        #[stc.STC_P_TRIPLE,       color.TRIPLE],
        #[stc.STC_P_TRIPLEDOUBLE, color.TRIPLEDOUBLE],
        #[stc.STC_P_WORD,         color.WORD],
    #]

    #for v in style:
        #self.StyleSetForeground(v[0], v[1])

    ##--Key words
    keyword = """and del from not while as elif global or with assert else if
                pass yield break except import print class exec in raise continue
                finally is return def for lambda try True False self None"""
    self.SetKeyWords(0, wxT(keyword))
    
#-------------------------------------------------------------------
def lua_lexer(self):
    doc = self
    doc.SetLexer(stc.STC_LEX_LUA)

    s = [
        [stc.STC_LUA_CHARACTER,   color.character, ""],
        [stc.STC_LUA_COMMENT,     color.comment, "Italic"],
        [stc.STC_LUA_COMMENTDOC,  color.commentblock, "Italic"],
        [stc.STC_LUA_COMMENTLINE, color.commentline, "Italic"],
        [stc.STC_LUA_DEFAULT,     color.default, ""],
        [stc.STC_LUA_IDENTIFIER,  color.identifier, ""],
        [stc.STC_LUA_LITERALSTRING, color.string, ""],
        [stc.STC_LUA_NUMBER,      color.number, ""],
        [stc.STC_LUA_OPERATOR,    color.operator, "Bold"],
        [stc.STC_LUA_PREPROCESSOR,color.preprocessor, ""],
        [stc.STC_LUA_STRING,      color.string, ""],
        [stc.STC_LUA_STRINGEOL,   color.stringeol, ""],
        [stc.STC_LUA_WORD,  color.word, "Bold"],
        [stc.STC_LUA_WORD2, color.word2, ""],
        [stc.STC_LUA_WORD3, color.word3, ""],
        [stc.STC_LUA_WORD4, color.word4, ""],
        [stc.STC_LUA_WORD5, color.word4, ""],
        [stc.STC_LUA_WORD6, color.word4, ""]
    ]

    for v in s:
        doc.StyleSetForeground(v[0], v[1])
        if v[2] == "Bold" :
            self.StyleSetBold(v[0], True)

    # Key words
    doc.SetKeyWords(0, wxT("function for while repeat until if else elseif end break return in do : switch case "))
    doc.SetKeyWords(1, wxT("local"))
    doc.SetKeyWords(2, wxT("and or not"))
    doc.SetKeyWords(3, wxT("None true False"))
        
def c_lexer(self):
    self.SetLexer(stc.STC_LEX_CPP)
    style = [
        [stc.STC_C_CHARACTER, color.character],
        [stc.STC_C_COMMENT, color.comment],
        [stc.STC_C_COMMENTDOC, color.commentdoc],
        [stc.STC_C_COMMENTDOCKEYWORD, color.commentdoc],
        [stc.STC_C_COMMENTDOCKEYWORDERROR, color.commentdoc],
        [stc.STC_C_COMMENTLINE, color.commentline],
        [stc.STC_C_COMMENTLINEDOC, color.commentdoc],
        [stc.STC_C_DEFAULT, color.default],
        [stc.STC_C_IDENTIFIER, color.identifier],
        [stc.STC_C_NUMBER, color.number],
        [stc.STC_C_OPERATOR, color.operator, "Bold"],
        [stc.STC_C_PREPROCESSOR, color.preprocessor],
        [stc.STC_C_REGEX, color.string],
        [stc.STC_C_STRING, color.string, "Bold"],
        [stc.STC_C_STRINGEOL, color.stringeol, "Bold"],
        [stc.STC_C_UUID, color.string],
        [stc.STC_C_VERBATIM, color.word1],
        [stc.STC_C_WORD, color.word, "Bold"],
        [stc.STC_C_WORD2, color.word2, "Bold"],
    ]

    for v in style:
        self.StyleSetForeground(v[0], v[1])
        
        if len(v) > 2:
            if v[2] == "Bold" :
                self.StyleSetBold(v[0], True)
            
    #--Key words
    self.SetKeyWords(0, wxT("for while repeat until if else elseif end break return in do struct class switch case static volatile extern"))
    self.SetKeyWords(1, wxT("unsigned signed void int short char long double float union typedef __sfr __at __interrupt"))
    self.SetKeyWords(2, wxT(""))
    self.SetKeyWords(3, wxT("NULL TRUE FALSE None true False"))

#-------------------------------------------------------------------
def js_lexer(self):
    style = [
        #stc.STC_LUA_CHARACTER = [7, color.character],
        #stc.STC_LUA_COMMENT = [1, color.COMMENT, "Italic"],
        #stc.STC_LUA_COMMENTDOC = [3, color.COMMENTBLOCK, "Italic"],
        #stc.STC_LUA_COMMENTLINE = [2, color.COMMENT, "Italic"],
        #stc.STC_LUA_DEFAULT = [0, color.DEFAULT],
        #stc.STC_LUA_IDENTIFIER = [11, color.identifier],
        #stc.STC_LUA_LITERALSTRING = [8, color.STRING],
        #stc.STC_LUA_NUMBER = [4, color.number],
        #stc.STC_LUA_OPERATOR = [10, color.operator, "Bold"],
        #stc.STC_LUA_PREPROCESSOR = [9, color.PREPROCESSOR],
        #stc.STC_LUA_STRING = [6, color.STRING],
        #stc.STC_LUA_STRINGEOL = [12, color.STRINGEOL],
        #stc.STC_LUA_WORD = [5, color.WORD, "Bold"],
        #stc.STC_LUA_WORD2 = [13, color.WORD2],
        #stc.STC_LUA_WORD3 = [14, color.WORD3],
        #stc.STC_LUA_WORD4 = [15, color.WORD4],
        #stc.STC_LUA_WORD5 = [16, color.WORD4],
        #stc.STC_LUA_WORD6 = [17, color.WORD4],
    ]
    for v in style:
        self.StyleSetForeground(v[0], v[1])

    #keyword = [[break case catch continue debugger default delete
                      #do else finally for def if in instanceof new
                      #return switch this throw try typeof var void while
                      #wit def ]]

    #--Key words
    #self.SetKeyWords(0, wxT(keyword))
    #self.SetKeyWords(1, wxT("void int short char long double float #include #define #typedef"))
    #self.SetKeyWords(2, wxT("__init__ self parent __main__"))
    #self.SetKeyWords(3, wxT("NULL TRUE FALSE None true False"))


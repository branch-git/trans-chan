import wx
import wx.lib.scrolledpanel
import pyperclip
import time
import urllib.parse
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep


class Translator:       #seleniumによる翻訳を定義するクラス
    def __init__(self):
        self.options = Options()
        self.options.binary_location =  "C:\\Program Files\\chrome-win\\chrome.exe"
        #self.options.add_argument("--headless")
        #self.options.add_argument("--proxy-server=https://proxy.funai.co.jp:3128")
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.minimize_window()
        self.browser.implicitly_wait(2)

    def trans(self, txt , lg1 , lg2):      # lg1からlg2に翻訳する関数

        # 翻訳したい文をURLに埋め込んでからアクセス
        text_for_url = urllib.parse.quote_plus(txt, safe='')
        url = "https://translate.google.co.jp/#{1}/{2}/{0}".format(text_for_url , lg1 , lg2)
        self.browser.get(url)

        # 少し待つ
        wait_time = len(text) / 100
        if wait_time < 0.5:
            wait_time = 0.5
        time.sleep(wait_time)

        # 翻訳結果を抽出
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        ret =  soup.find(class_="tlid-translation translation")

        return ret.text    

    def quit(self):
        self.browser.quit()


def main():
    # クリップボードの内容を取得
    orig = str(pyperclip.paste())

    # 改行を検出して分割．この際改行情報"\r\n"は失われる
    orignal_elements = orig.splitlines()
    print(orignal_elements)
    # 翻訳対象の日本語を格納する変数
    origs = []

    # 空白行を取得するためのグローバル変数
    global blank_row
    blank_row = []
    count = 0
    while count < len(orignal_elements):
        buf = orignal_elements[count]           #"   "のような空白のみの要素を抹殺
        buf = buf.replace(" " , "")             #単にスペースを消すだけでは外国語に対応できないので，差分をとる
        if buf != "":                           #空白でない場合は翻訳対象に追加
            origs.append(orignal_elements[count])
        else:
            blank_row.append(count)             #空白の場合はもともと空白行だったので，要素の場所をintで取得
        count += 1
    
    # 翻訳する2言語を設定[母国語,外国語]    将来的にプルダウンから言語を選択できるように構築する予定．
    global lg
    lg = ["ja" , "en"]

    # 逆翻訳にする二言語を設定 [外国語,日本語]
    global rev_lg
    rev_lg = list(reversed(lg))

    # GUIの準備
    app = wx.App()

    # 読み込み中の表示
    read_frame = wx.Frame(None, wx.ID_ANY, "翻訳中...", size=(250,0))
    #read_panel = wx.Panel(read_frame)
    #read_text = wx.TextCtrl(read_panel,wx.ID_ANY, "翻訳中...",style = wx.TE_CENTER)
    # = wx.BoxSizer(wx.HORIZONTAL)
    #read_layout.Add(read_text,flag = wx.EXPAND)
    #read_panel.SetSizer(read_layout)
    #read_text.Disable()
    read_frame.Centre() #中央に表示
    read_frame.Show()

    size = (900,600)
    global frame
    frame = wx.Frame(None, wx.ID_ANY, '翻訳ちゃん', size=size)
    panel = wx.lib.scrolledpanel.ScrolledPanel(frame,-1, size=size, pos=(0,28), style=wx.SIMPLE_BORDER)
    panel.SetupScrolling()
    panel.SetBackgroundColour('#AFAFAF')

    global rows
    global text
    global en_text
    global jp_text
    global btn
    rows = len(origs)           #lenは0を含むため，行数に注意
    layout = wx.FlexGridSizer(rows+1,4,0,0)

    text = [""]*rows            #原文テキストウィジェットの準備
    en_text = [""]*rows         #英文テキストウィジェットの準備
    jp_text = [""]*rows         #再訳文テキストウィジェットの準備
    btn = [""]*rows             #翻訳ボタンウィジェットの準備

    cellsize = (270,90)
    for row in range(rows):
        #原文
        txt = origs[row]
        text[row] = wx.TextCtrl(panel, row , txt, style = wx.TE_MULTILINE,size=cellsize)
        #print("原文：",txt)

        #英文
        en_txt = translator.trans(origs[row], *lg)
        en_text[row] = wx.TextCtrl(panel, row , en_txt, style = wx.TE_MULTILINE,size=cellsize)
        en_text[row].Disable()      #書き込み禁止
        #print("英文：",en_txt)

        #再翻訳
        jp_txt = translator.trans(en_txt, *rev_lg)
        jp_text[row] = wx.TextCtrl(panel, row , jp_txt, style = wx.TE_MULTILINE,size=cellsize)
        jp_text[row].Disable()      #書き込み禁止
        #print("再翻訳文：",jp_txt)

        #翻訳ボタン
        btn[row] = wx.Button(panel, row, "翻訳", size=(60, 40))
        btn[row].Bind(wx.EVT_BUTTON, OnClickBtn)            #ボタンをイベントにバインド


        #ウィジェットの配置
        #layout.Add(text[row], flag=wx.ALIGN_LEFT | wx.GROW)         #原文
        layout.Add(text[row], flag=wx.SHAPED)         #原文
        layout.Add(jp_text[row], flag=wx.SHAPED)      #再翻訳
        layout.Add(en_text[row], flag=wx.SHAPED)      #英文        
        layout.Add(btn[row],flag=wx.SHAPED | 
            wx.ALIGN_CENTER_VERTICAL | wx.TE_MULTILINE)             #翻訳ボタン
    
    copy_btn = wx.Button(panel, wx.ID_ANY, "翻訳完了", size=(80, 40))
    copy_btn.Bind(wx.EVT_BUTTON, OnClickCopyBtn)
    layout.Add(copy_btn,flag=wx.SHAPED | 
        wx.ALIGN_CENTER_VERTICAL | wx.TE_MULTILINE)

    retrans_btn = wx.Button(panel, wx.ID_ANY, "各セルをリセットして再翻訳", size=(200, 40))
    retrans_btn.Bind(wx.EVT_BUTTON, OnClickRetransBtn)
    layout.Add(retrans_btn,flag=wx.SHAPED | 
        wx.ALIGN_CENTER_VERTICAL | wx.TE_MULTILINE)
    
    exit_btn = wx.Button(panel, wx.ID_ANY, "翻訳ちゃんを終了", size=(120, 40))
    exit_btn.Bind(wx.EVT_BUTTON, OnClickExitBtn)
    layout.Add(exit_btn,flag=wx.SHAPED | 
        wx.ALIGN_CENTER_VERTICAL | wx.TE_MULTILINE)

    # ボタンの配置
    layout.AddGrowableCol(0, 3)
    layout.AddGrowableCol(1, 3)
    layout.AddGrowableCol(2, 3)
    layout.AddGrowableCol(3, 1)

    # レイアウトの更新
    panel.SetSizer(layout)

    # ステータスバーを定義
    frame.CreateStatusBar()
    frame.SetStatusText("オンラインサービス利用のため守秘義務を遵守の上ご利用ください")
    
    read_frame.Close()
    frame.Centre() #中央に表示
    frame.Show()
    app.MainLoop()


def OnClickBtn(event):
    num = event.GetId()

    btn[num].Disable()
    
    n_txt = text[num].GetValue()
    n_en_txt = translator.trans(n_txt, *lg)
    n_jp_txt = translator.trans(n_en_txt, *rev_lg)
    
    en_text[num].SetValue(n_en_txt)
    jp_text[num].SetValue(n_jp_txt)

    btn[num].Enable()

def copy_all():         #翻訳結果の英文をクリップボードにコピーする関数

    fin_txt = ""        # クリップボードにコピーする文字列 
    fin_txts = []       # 翻訳後の英文をセルごとに格納する文字列

    for row in range(rows):
        fin_txts.append(en_text[row].GetValue()+"\r\n")     #splitlinesメソッドで失われた改行情報を復元

    for blank in blank_row:
        fin_txts.insert(blank,"\r\n")                       #空白行の場所はblank_rowに格納されているので空白行を追加

    for element in fin_txts:
        fin_txt += element                                  #改行情報を復元したので出力用文字列として結合

    return fin_txt

def OnClickCopyBtn(event):          #【翻訳完了】ボタンが押された場合
    pyperclip.copy(copy_all())

def OnClickRetransBtn(event):       #【各セルをリセットして再翻訳】ボタンが押された場合
    frame.Close()
    main()

def OnClickExitBtn(event):          #【翻訳ちゃんを終了】ボタンが押された場合
    pyperclip.copy(copy_all())
    frame.Close()
    translator.quit()


if __name__ == "__main__":
    translator=Translator()
main()


"""ネタ帳
・コンボボックス
https://www.python-izm.com/gui/wxpython/wxpython_combobox/
    →言語選択
・単語帳など
・各セルのリサイズ
・行追加ボタン

win10 64bit用chromium
https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win_x64%2F768952%2Fchrome-win.zip?generation=1589490546798193&alt=media
これをprogramfiles直下に移動
pip install chromedriver_binary==84.0.4147.30.0
"""
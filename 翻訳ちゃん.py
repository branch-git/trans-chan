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


def main():
    #クリップボードの内容を取得
    orig = str(pyperclip.paste())
    #orig = "splitに関連したメソッドで、rsplitというメソッドがあります。こちらは、splitの文字区切りを逆から行っていく働きをします。注意点として、rsplitは右から区切りますが、リストに代入される順番は変わらず左からとなります。基本編でURLを回数を指定して区切りましたが、それをrsplitで区切って確認しましょう。"
    origs = orig.split("。") 

    #GUIの準備
    app = wx.App()
    size = (900,600)
    # size=screenSize
    global frame
    frame = wx.Frame(None, wx.ID_ANY, '翻訳ちゃん', size=size)
    #panel = wx.Panel(frame, wx.ID_ANY)
    panel = wx.lib.scrolledpanel.ScrolledPanel(frame,-1, size=size, pos=(0,28), style=wx.SIMPLE_BORDER)
    panel.SetupScrolling()
    panel.SetBackgroundColour('#AFAFAF')


    global rows
    global en_text
    rows = len(origs)           #lenは0を含むため，行数に注意
    layout = wx.FlexGridSizer(rows,4,0,0)

    text = [""]*rows            #原文テキストウィジェットの準備
    en_text = [""]*rows         #英文テキストウィジェットの準備
    jp_text = [""]*rows         #再訳文テキストウィジェットの準備
    btn = [""]*rows             #翻訳ボタンウィジェットの準備

    cellsize = (270,90)
    for row in range(rows-1):
        #原文
        txt = origs[row]+"。"
        text[row] = wx.TextCtrl(panel, row , txt, style = wx.TE_MULTILINE,size=cellsize)
        #print("原文：",txt)

        #英文
        en_txt = translator.jp2entrans(origs[row]+"。")
        en_text[row] = wx.TextCtrl(panel, row , en_txt, style = wx.TE_MULTILINE,size=cellsize)
        en_text[row].Disable()      #書き込み禁止
        #print("英文：",en_txt)

        #再翻訳
        jp_txt = translator.en2jptrans(en_txt)
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

    layout.AddGrowableCol(0, 3)
    layout.AddGrowableCol(1, 3)
    layout.AddGrowableCol(2, 3)
    layout.AddGrowableCol(3, 1)

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

    panel.SetSizer(layout)

    frame.CreateStatusBar()
    frame.SetStatusText("オンラインサービス利用のため守秘義務を遵守の上ご利用ください")
    frame.Centre() #中央に表示
    frame.Show()
    app.MainLoop()


def OnClickBtn(event):
    num = event.GetId()

    btn[num].Disable()
    n_txt = text[num].GetValue()
    
    n_en_txt = translator.jp2entrans(n_txt)
    en_text[num].Enable()
    en_text[num].SetValue(n_en_txt)
    en_text[num].Disable()
    
    n_jp_txt = translator.en2jptrans(n_en_txt)
    jp_text[num].Enable()
    jp_text[num].SetValue(n_jp_txt)
    jp_text[num].Disable()

    btn[num].Enable()

def copy_all():
    fin_txt = ""
    for row in range(rows-1):
        fin_txt += en_text[row].GetValue()
    return fin_txt

def OnClickCopyBtn(event):
    pyperclip.copy(copy_all())

def OnClickRetransBtn(event):
    frame.Close()
    main()

def OnClickExitBtn(event):
    pyperclip.copy(copy_all())
    frame.Close()
    translator.quit()

class Translator:       #seleniumによる翻訳部分
    def __init__(self):
        self.options = Options()
        self.options.binary_location =  "C:\\Program Files\\chrome-win\\chrome.exe"
        #self.options.add_argument("--headless")
        #self.options.add_argument("--proxy-server=http://proxy.funai.co.jp")
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.minimize_window()
        self.browser.implicitly_wait(2)

    def en2jptrans(self, text):

        # 翻訳したい文をURLに埋め込んでからアクセスする
        text_for_url = urllib.parse.quote_plus(text, safe='')
        url = "https://translate.google.co.jp/#en/ja/{0}".format(text_for_url)
        self.browser.get(url)

        # # 数秒待機する（大量の文書を連続して翻訳するときはコメントアウトしてください）
        wait_time = len(text) / 50
        time.sleep(wait_time)

        # 翻訳結果を抽出する
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        ret =  soup.find(class_="tlid-translation translation")

        return ret.text

    def jp2entrans(self, text):

        # 翻訳したい文をURLに埋め込んでからアクセスする
        text_for_url = urllib.parse.quote_plus(text, safe='')
        url = "https://translate.google.co.jp/#ja/en/{0}".format(text_for_url)
        self.browser.get(url)

        # # 数秒待機する（大量の文書を連続して翻訳するときはコメントアウトしてください）
        wait_time = len(text) / 50
        time.sleep(wait_time)

        # 翻訳結果を抽出する
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        ret =  soup.find(class_="tlid-translation translation")

        return ret.text

    def quit(self):
        self.browser.quit()


if __name__ == "__main__":
    translator=Translator()
main()


"""ネタ帳
・コンボボックス
https://www.python-izm.com/gui/wxpython/wxpython_combobox/
    →言語選択
・区切り文字で？などに対応
・単語帳など
・常駐モード
・各セルのリサイズ
・行追加ボタン

win10 64bit用chromium
https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win_x64%2F768952%2Fchrome-win.zip?generation=1589490546798193&alt=media
これをprogramfiles直下に移動
pip install chromedriver_binary==84.0.4147.30.0
"""
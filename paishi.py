
# 2020.4.24 0:13
# コマンド実行時に管理者権限が必要
# pythonファイルがあるディレクトリへの移動が必要
# CSVデータはpythonファイルと同じディレクトリに必要

# 2020.4.24 1:42
# 以下でサイズ指定を行う
# (c)が表示できないフォント用に一文字目を置き換えられる

# 2020.4.24 14:00
# CSVデータ名はコンソールで入力
# CSVデータはUTF-8である必要がある
# 文字列"answer"を含むCSVデータは解答データとして認識
# 問題データは本文が指定行数まで表示され、超えれば[...]を表示 詳細はないものとして仮定
# 解答データは本文、詳細ともに指定行数まで表示され、超えれば[...]を表示
# 行間は四行時に揃えて設定してあり、変更可

# 2020.4.25 21:00
# numpyが必要
# 牌画中にstroke.pngを追加
# 本文・詳細中に牌記号を書くことで画像を表示
# (連続で4p4p4p5p5pなどと入力すると幅にバグが発生)
# それに伴い[...]を表示する機能は一旦廃止

# 2020.4.27 14:27
# タイトル及びサブタイトルを白文字に変更
# ツモ牌がドラの場合にツモ牌にも王冠を描画
# フッターを省略時、フッターには(c)麻雀ドリルと記述

# 2020.4.30 9:28
# ●●局●家●巡目を形だけ追加・重なることがありえます
# 問題タイトルを黒色、解答タイトルを白色に変更
# 本文および詳細中に牌を使ってもずれなくなりました
# リファクタリング未完
# 画像幅が変更できなくなっています 650pxでのみ使えます

# 2020.5.8 23:16
# 650px四方以外は対応していません
# 場況が何文字でも大丈夫になりました(重なりません)
# 詳細のフォントを2px増加
# 詳細の牌画の位置を調整
# 解答データの際は牌姿が上、本文詳細が下にくる
# 解答データの詳細を最大８行に設定
# 一行に入る文字数の目安:　■:26文字　ひらがな:26文字  a:45文字  牌画:24個
# ↑ 全角文字ならおおよそ一行に26文字と考えてよさそうです。

# 2020.5.23 22:38
# ツモの部分を空白文字列にした場合、ツモの文字とツモ牌を描画しないように設定

# 2020.5.29 23:40
# アンダーバー"_"を本文または詳細で用いた場合、改行を行う

# 2020.6.13
# 文章中に牌姿を記述する際、「45567p」のように連続していても牌として認識可能なように修正

# 2020.6.17
# 汎用クラスを分離

from PIL import Image, ImageDraw, ImageFont
import os
import csv
import numpy as np
import drillcommon as drc
answerstring = []

# 出力するフォルダ
stOutputPath = "Output_paishi/"

# フォントデータ
stFontName = 'Fonts/YuGothB.ttc'


# 画像の幅および高さpxを指定 (nPicWidth = 650)
nPicWidth = 650
cm = drc.DrillCommon(nPicWidth,stFontName)

# 本文・詳細の余白を指定 (nMainMargin,nDetailMargin = 30,30)
nMainMargin,nDetailMargin = 30,30
# 本文の行間・詳細の行間を指定(nMainInterval,nDetailInterval = 25,14)
nMainInterval,nDetailInterval = 25,14

# 解答の時にどれだけ牌姿を移動させるか Y
nDifAnswerScenePosY = -200
# 解答の時にどれだけ本文と詳細を移動させるか Y
nDifAnswerTextPosY = 175

# 最大行を指定 (nMainMaxRow,nAnswerModeMainMaxRow,nAnswerModeDetailMaxRow = 4,1,8)
nMainMaxRow,nAnswerModeMainMaxRow,nAnswerModeDetailMaxRow = 4,1,8

# 含まれていると解答データであると認識される文字列リスト（追加可）
# 例:answerstring.append("kaitou")
answerstring.append("answer")
# 一文字目を(c)に書き換える
bReplaceFirstCharToCopyRight = False
#「ドラ」の欄の文字列がドラ表示牌のことであるならTrue
bDoraIsDoraIndicator = True

# CSVデータのファイル名を指定
print('読み込むCSVデータ名を入力(.csvは省略)')
stInput = input('>> ')
stCSVfileName = stInput
if not os.path.isfile(stCSVfileName + ".csv"):
    print("CSVデータが存在しません")
    quit()
# CSVデータのファイル名を指定
stCSVPath = stCSVfileName + ".csv"

bIsAnswerData = False
for st in answerstring:
    if st in stCSVfileName:
        bIsAnswerData = True

with open(stCSVfileName + '.csv',encoding = "utf-8_sig") as f:

    print ("\n読み込みCSVファイル名 : " + stCSVfileName +"\n")
    if bIsAnswerData:
        print ("このCSVは、解答 として処理します\n")
    else:
        print ("このCSVは、問題 として処理します\n")
    
    reader = csv.reader(f)
    for rowcount,row in enumerate(reader):
        print ( str(rowcount).zfill(3) + " 行目を処理中...")

        if len(row) == 0:
            print("       該当行のデータがありません")
            continue
        elif len(row) < 8:
            print("       該当行の文章データが不足しています")
            continue

        stTitle,stSubTitle,stMain,stDetail,stBakaze,stKyoku,stJikaze,stJunme = row[0:8]

        if len(row) < 11:
            print("       該当行の局面データが不足しています")
            continue

        stDora,stTehai,stTsumoPai = row[8:11]

        # 行検査
        if stTitle == "タイトル":
            continue

        # 背景の描画
        if bIsAnswerData:
            imBase = Image.new('RGB',(nPicWidth,nPicWidth),(255,255,255,255))
            ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.000), (nPicWidth*1.000, nPicWidth*0.100)], fill=(255,87,87), outline='white',  width=0)
            ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.100), (nPicWidth*1.000, nPicWidth*0.377)], fill=(254,229,189), outline='white',  width=0)
            ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.109, nPicWidth*0.940), (nPicWidth*0.891, nPicWidth*0.943)], fill=(40,40,40), outline='white',  width=0)
        else:
            imBase = Image.new('RGB',(nPicWidth,nPicWidth),(255,255,255,255))
            ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.000), (nPicWidth*1.000, nPicWidth*0.100)], fill=(201,226,101), outline='white',  width=0)
            ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.418), (nPicWidth*1.000, nPicWidth*0.695)], fill=(254,229,189), outline='white',  width=0)
            ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.109, nPicWidth*0.940), (nPicWidth*0.891, nPicWidth*0.943)], fill=(40,40,40), outline='white',  width=0)
        
        imBase = imBase.resize(size=(nPicWidth,nPicWidth))
        draw = ImageDraw.Draw(imBase)


        # フッターの整理
        stFooter = row[11] if len(row) > 11 else ""
        if stFooter == "":
            stFooter = "©麻雀ドリル"
        elif bReplaceFirstCharToCopyRight:
            stFooter = "(C)" + stFooter[1:]
        # タイトル、サブタイトル、フッターの描画
        SubTitle_width = draw.textsize(stSubTitle,font=ImageFont.truetype(stFontName,cm.fixScale(25)))[0]
        Footer_width = draw.textsize(stFooter,font=ImageFont.truetype(stFontName,cm.fixScale(25)))[0]

        draw.text((cm.fixScale(20),cm.fixScale(20)),stTitle,font=ImageFont.truetype(stFontName,cm.fixScale(30)),\
            fill=(bIsAnswerData*255,bIsAnswerData*255,bIsAnswerData*255,255))
        draw.text((nPicWidth - SubTitle_width-cm.fixScale(20),cm.fixScale(25)),stSubTitle,\
            font=ImageFont.truetype(stFontName,cm.fixScale(25)),fill=(bIsAnswerData*255,bIsAnswerData*255,bIsAnswerData*255,255))
        draw.text(((nPicWidth - Footer_width)/2,cm.fixScale(615)),stFooter,font=ImageFont.truetype(stFontName,cm.fixScale(25)),fill=(0,0,0,255))

       
        # 本文・詳細の整理
        prtMain_info = cm.stringToParts(stMain,25,32,43,0,10,0,nMainInterval,0,bIsAnswerData*nDifAnswerTextPosY+95,nMainMargin,True)
        prtDetail_info = cm.stringToParts(stDetail,22,26,34,0,6,0,nDetailInterval,0,bIsAnswerData*nDifAnswerTextPosY+145,nDetailMargin,True)
        # 本文・詳細の描画
        if bIsAnswerData:
            cm.drawPartsToImg(imBase,prtMain_info,32,43,25,nAnswerModeMainMaxRow,0)
            cm.drawPartsToImg(imBase,prtDetail_info,26,34,22,nAnswerModeDetailMaxRow,0)
        else:
            cm.drawPartsToImg(imBase,prtMain_info,32,43,25,nMainMaxRow,0)

        # 場況文字列を整理
        stBakyou = ""
        if stBakaze != "":
            stBakyou += stBakaze
        if stKyoku != "":
            stBakyou += stKyoku + "局 "
        if stJikaze != "":
            stBakyou += stJikaze + "家 "
        if stJunme != "":
            stBakyou += stJunme + "巡目 "
        doraSrcNum,doraNum,doraSuit = cm.drPaiInfo(stDora,bDoraIsDoraIndicator)
        stDoraTitle = "ドラ表示牌" if bDoraIsDoraIndicator else "ドラ"
        stBakyou += stDoraTitle + " " + str(doraSrcNum) + doraSuit
        # 場況文字列の描画
        prtBakyo_info = cm.stringToParts(stBakyou,25,35,47,0,13,0,0,0,bIsAnswerData*nDifAnswerScenePosY+300,30,True)
        cm.drawPartsToImg(imBase,prtBakyo_info,35,47,25,1,0)

        # "ツモ"
        if stTsumoPai != "":
            draw.text((cm.fixScale(590),bIsAnswerData*cm.fixScale(nDifAnswerScenePosY)+cm.fixScale(330)),"ツモ",\
                font=ImageFont.truetype(stFontName,cm.fixScale(20)),fill=(0,0,0,255))
        # 手牌描画
        prtTehai = cm.stringToParts(stTehai+"   "+stTsumoPai,15,43,57,0,0,0,0,22+57,bIsAnswerData*nDifAnswerScenePosY+380,18,False,str(doraNum)+str(doraSuit))
        cm.drawPartsToImg(imBase,prtTehai,42,57,10,1,0)


        # 画像の出力
        os.makedirs(stOutputPath, exist_ok=True)
        imBase.save(stOutputPath + stCSVfileName + "_" + str(rowcount).zfill(3) + ".jpg")

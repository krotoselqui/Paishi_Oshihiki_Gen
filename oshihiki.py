
# コマンド実行時に管理者権限が必要
# pythonファイルがあるディレクトリへの移動が必要
# CSVデータはpythonファイルと同じディレクトリに必要

# 2020.6.17
# 全体のサイズ指定およびフォント指定はこのファイルで行う
# 副露は遠いほうから順番に生成
# mpszの直後に、リーチ時用にr、手出し用にn、ツモ切用にt、副露用にfが予約されている
#   用いる際は空白をあけることで回避できる
# _または＿で改行を行う
# 問題はX_Q000.jpg 解答はX_A000.jpgというフォーマットで出力される
# このファイルの編集は、paishi.pyには影響しない
# paishi.pyとoshihiki.pyいずれも画像幅は可変

# 2020.6.18
# 手出しの赤枠の太さを13px（ソース）に変更
# 捨て牌が一列、二列のときに真ん中寄りになるように変更
# 鳴いた牌および捨て牌に枠を追加

from PIL import Image, ImageDraw, ImageFont
import os
import csv
import numpy as np
import drillcommon as drc
answerstring = []

def insertFuroCond(stFuro):
    ankancode = "9z"
    furocode = 'f'
    for char in stFuro:
        if furocode.find(char) != -1:
            return stFuro
    for count in range(0,len(stFuro)-1):
        if stFuro[count:count+2] == ankancode:
            return stFuro
    if len(stFuro)<6:
        return ""
    return stFuro[0:2] + "f" + stFuro[2:6]

# 出力するフォルダ
stOutputPath = "Output_oshihiki/"

# フォントデータ
stFontName = 'Fonts/YuGothB.ttc'


# 画像の幅および高さpxを指定 (nPicWidth = 650)
nPicWidth = 650
cm = drc.DrillCommon(nPicWidth,stFontName)

# 本文・詳細の余白を指定 (nMainMargin,nDetailMargin = 30,30)
# nMainMargin,nDetailMargin = 30,30
nQuestionMargin,nDetailMargin = 30,30
# 本文の行間・詳細の行間を指定(nMainInterval,nDetailInterval = 25,14)
# nMainInterval,nDetailInterval = 25,14
nQuestionInterval,nDetailInterval = 16,14


# 解答の時にどれだけ牌姿を移動させるか Y
nDifAnswerScenePosY = -200
# 解答の時にどれだけ本文と詳細を移動させるか Y
nDifAnswerTextPosY = 175

# 最大行を指定 (nMainMaxRow,nAnswerModeMainMaxRow,nAnswerModeDetailMaxRow = 4,1,8)
# nMainMaxRow,nAnswerModeMainMaxRow,nAnswerModeDetailMaxRow = 4,1,8
# 最大行を指定 
nQuestionMaxRow,nDetailMaxRow = 4,4

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


with open(stCSVfileName + '.csv',encoding = "utf-8_sig") as f:

    print ("\n読み込みCSVファイル名 : " + stCSVfileName +"\n")
    
    reader = csv.reader(f)
    for rowcount,row in enumerate(reader):
        print ( str(rowcount).zfill(3) + " 行目を処理中...")

        if len(row) == 0:
            print("       該当行のデータがありません")
            continue


        # elif len(row) < 8:
        #    print("       該当行の文章データが不足しています")
        #    continue
        # stTitle,stSubTitle,stMain,stDetail,stBakaze,stKyoku,stJikaze,stJunme = row[0:8]

        # if len(row) < 11:
        #    print("       該当行の局面データが不足しています")
        #    continue
        # stDora,stTehai,stTsumoPai = row[8:11]

        stTitle,stSubTitle,stDiscard,stFuro1,stFuro2,stFuro3 = row[0:6]
        stQuestion,stAnswer,stDetail,stBakaze,stKyoku,stJikaze,stJunme = row[6:13]
        stDora,stTehai,stTsumoPai = row[13:16]

        # 行検査
        if stTitle == "タイトル":
            continue

        for QandA in range(0,2):
            bIsAnswerData = (QandA != 0)

            if bIsAnswerData == False:

                # [Q]背景の描画
                imBase = Image.new('RGB',(nPicWidth,nPicWidth),(255,255,255,255))
                ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.000), (nPicWidth*1.000, nPicWidth*0.100)], fill=(201,226,101), outline='white',  width=0)
                ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.100), (nPicWidth*1.000, nPicWidth*0.406)], fill=(254,229,189), outline='white',  width=0)
                ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.406), (nPicWidth*1.000, nPicWidth*0.683)], fill=(217,217,217), outline='white',  width=0)
                ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.109, nPicWidth*0.940), (nPicWidth*0.891, nPicWidth*0.943)], fill=(40,40,40), outline='white',  width=0)
                
                imBase = imBase.resize(size=(nPicWidth,nPicWidth))
                draw = ImageDraw.Draw(imBase)

                # [Q]フッターの整理
                stFooter = row[16] if len(row) > 16 else ""
                if stFooter == "":
                    stFooter = "©麻雀ドリル"
                elif bReplaceFirstCharToCopyRight:
                    stFooter = "(C)" + stFooter[1:]
                # [Q]タイトル、サブタイトル、フッターの描画
                SubTitle_width = draw.textsize(stSubTitle,font=ImageFont.truetype(stFontName,cm.fixScale(25)))[0]
                Footer_width = draw.textsize(stFooter,font=ImageFont.truetype(stFontName,cm.fixScale(25)))[0]

                draw.text((cm.fixScale(20),cm.fixScale(20)),stTitle,font=ImageFont.truetype(stFontName,cm.fixScale(30)),\
                    fill=(bIsAnswerData*255,bIsAnswerData*255,bIsAnswerData*255,255))
                draw.text((nPicWidth - SubTitle_width-cm.fixScale(20),cm.fixScale(25)),stSubTitle,\
                    font=ImageFont.truetype(stFontName,cm.fixScale(25)),fill=(bIsAnswerData*255,bIsAnswerData*255,bIsAnswerData*255,255))
                draw.text(((nPicWidth - Footer_width)/2,cm.fixScale(615)),stFooter,font=ImageFont.truetype(stFontName,cm.fixScale(25)),fill=(0,0,0,255))

                # [Q]問題文の描画
                prtQuestion_info = cm.stringToParts(stQuestion,22,26,34,0,6,0,nQuestionInterval,0,463,nQuestionMargin,True)
                cm.drawPartsToImg(imBase,prtQuestion_info,26,34,22,nQuestionMaxRow,0)

            else:

                # [A]背景の描画・解答
                imBase = Image.new('RGB',(nPicWidth,nPicWidth),(255,255,255,255))
                ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.000), (nPicWidth*1.000, nPicWidth*0.100)], fill=(255,87,87), outline='white',  width=0)
                ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.100), (nPicWidth*1.000, nPicWidth*0.406)], fill=(254,229,189), outline='white',  width=0)
                ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.000, nPicWidth*0.406), (nPicWidth*1.000, nPicWidth*0.666)], fill=(217,217,217), outline='white',  width=0)
                # ImageDraw.Draw(imBase).rectangle([(nPicWidth*0.109, nPicWidth*0.940), (nPicWidth*0.891, nPicWidth*0.943)], fill=(40,40,40), outline='white',  width=0)
                
                imBase = imBase.resize(size=(nPicWidth,nPicWidth))
                draw = ImageDraw.Draw(imBase)

                # [A]タイトル及びサブタイトルの描画
                draw.text((cm.fixScale(20),cm.fixScale(20)),stTitle,font=ImageFont.truetype(stFontName,cm.fixScale(30)),\
                    fill=(bIsAnswerData*255,bIsAnswerData*255,bIsAnswerData*255,255))
                draw.text((nPicWidth - SubTitle_width-cm.fixScale(20),cm.fixScale(25)),stSubTitle,\
                    font=ImageFont.truetype(stFontName,cm.fixScale(25)),fill=(bIsAnswerData*255,bIsAnswerData*255,bIsAnswerData*255,255))
                # draw.text(((nPicWidth - Footer_width)/2,cm.fixScale(615)),stFooter,font=ImageFont.truetype(stFontName,cm.fixScale(25)),fill=(0,0,0,255))

                # [A]解答の描画
                prtAnswer_info = cm.stringToParts(stAnswer,25,32,43,0,10,0,25,0,455,30,True)
                cm.drawPartsToImg(imBase,prtAnswer_info,32,43,25,1,0)
                # [A]詳細の描画
                prtDetail_info = cm.stringToParts(stDetail,22,26,34,0,6,0,nDetailInterval,0,510,nDetailMargin,True)
                cm.drawPartsToImg(imBase,prtDetail_info,26,34,22,nDetailMaxRow,0)


            # （共通）捨て牌の描画
            prtDiscard_info = cm.stringToParts(stDiscard,30,35,46,0,0,0,35,999,405,211,True)
            r = cm.getMaxRowOfParts(prtDiscard_info)
            for prt in prtDiscard_info:
                prt.posY += (2-r) * cm.fixScale(28)
            cm.drawPartsToImg(imBase,prtDiscard_info,33,44,22,3,180)

            # （共通）ツモ切りの説明
            draw.text(((cm.fixScale(530),cm.fixScale(80+10))),"ツモ切り牌",font=ImageFont.truetype(stFontName,cm.fixScale(14)),fill=(0,0,0,255))
            prtTsumogiri = cm.stringToParts("5zt",30,30,40,0,0,0,0,100,100,0,True)
            prtTsumogiri[0].posX,prtTsumogiri[0].posY = cm.fixScale(552),cm.fixScale(104+10)
            cm.drawPartsToImg(imBase,prtTsumogiri,30,40,22,1,0)

            # （共通）副露の描画
            if stFuro1 != "":
                #stFuro = stFuro3[0:2] + "f" + stFuro3[2:6] if stFuro3 != "" else ""
                stFuro = insertFuroCond(stFuro3) if stFuro3 != "" else ""
                stFuro += "_" 
                stFuro += insertFuroCond(stFuro2) if stFuro2 != "" else ""
                stFuro += "_" 
                stFuro += insertFuroCond(stFuro1)
                prtFuro_info = cm.stringToParts(stFuro,30,33,44,0,0,0,30,999,405,210,True)
                for p in prtFuro_info:
                    p.posX += cm.fixScale(270)
                    p.posY += cm.fixScale(30)
                cm.drawPartsToImg(imBase,prtFuro_info,33,44,22,3,180)

            # （共通）鳴き手出しの説明
            if cm.hasNakiTedashi(prtDiscard_info):
                draw.text(((cm.fixScale(525),cm.fixScale(180-10))),"鳴き手出し牌",font=ImageFont.truetype(stFontName,cm.fixScale(14)),fill=(0,0,0,255))
                prtNakiTedashi = cm.stringToParts("5zn",30,30,40,0,0,0,0,100,100,0,True)
                prtNakiTedashi[0].posX,prtNakiTedashi[0].posY = cm.fixScale(552),cm.fixScale(204-10)
                cm.drawPartsToImg(imBase,prtNakiTedashi,30,40,22,1,0)

            # （共通）場況文字列を整理
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
            # （共通）場況文字列の描画
            prtBakyo_info = cm.stringToParts(stBakyou,25,35,47,0,13,0,0,0,300,30,True)
            cm.drawPartsToImg(imBase,prtBakyo_info,35,47,25,1,0)

            # （共通）"ツモ"
            if stTsumoPai != "":
                draw.text((cm.fixScale(590),cm.fixScale(310)),"ツモ",\
                    font=ImageFont.truetype(stFontName,cm.fixScale(20)),fill=(0,0,0,255))
            # （共通）手牌描画
            prtTehai = cm.stringToParts(stTehai+"   "+stTsumoPai,15,43,57,0,0,0,0,22+57,365,18,False,str(doraNum)+str(doraSuit))
            cm.drawPartsToImg(imBase,prtTehai,42,57,10,1,0)

            if bIsAnswerData == False:
                # 画像の出力
                os.makedirs(stOutputPath, exist_ok=True)
                imBase.save(stOutputPath + stCSVfileName + "_Q" + str(rowcount).zfill(3) + ".jpg")
            else:
                # 画像の出力
                # os.makedirs(stOutputPath, exist_ok=True)
                imBase.save(stOutputPath + stCSVfileName + "_A" + str(rowcount).zfill(3) + ".jpg")
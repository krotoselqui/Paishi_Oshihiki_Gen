from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np

numbers = '0123456789'
suits = 'mpsz'

funcs = 'rtnf'
charForNewLine = '_＿'

# 牌画データフォルダ
stPaigaFolderPath = "Paiga/"
# ドラ王冠を用意
stCrownPath = stPaigaFolderPath + "crown.png"
# 牌の枠を用意
stStrokePath = stPaigaFolderPath + "stroke.png",stPaigaFolderPath + "strokebold.png"


class draw_parts:
    def __init__(self,width,contents,isPai,row,posX,posY,reechOn = False,crownOn = False,darken = False,strokeOn = True,strokeColor = "Gray"):
        self.width = width
        self.contents = contents
        self.isPai = isPai
        self.row = row
        self.posX = posX
        self.posY = posY
        if (reechOn == True):
            self.rot = 90
        else:
            self.rot = 0
        self.crownOn = crownOn
        self.darken = darken
        self.strokeOn = strokeOn
        self.strokeColor = strokeColor

class DrillCommon():

    def __init__(self,nPicWidth,stFontName):
        self.nPicWidth = nPicWidth
        self.stFontName = stFontName

    def fixScale(self,a):
        return int(float(self.nPicWidth*a/650))

    def drPaiInfo(self,stDora,bDoraIsDoraIndicator):

        # ドラを調査
        if suits.find(stDora[-1:]) >= 0 and stDora != "":
            doraSuit = stDora[-1:]
        else:
            doraSuit = "z"

        if numbers.find(stDora[:1]) >= 0 and stDora != "":
            doraSrcNum = int(stDora[:1])
            doraNum = doraSrcNum
        else:
            doraSrcNum = 8
            doraNum = 8

        # ドラ表示牌のほうを用いているとき
        if bDoraIsDoraIndicator:

            if stDora == "8z" or stDora == "9z":
                doraNum = doraSrcNum
                doraSuit = "z"

            elif suits.find(doraSuit) != -1 and numbers.find(str(doraSrcNum)) != -1: 
                # 風牌
                if doraSuit == "z" and doraSrcNum >= 1 and doraSrcNum <= 4:
                    doraNum = doraSrcNum % 4 + 1
                # 三元牌
                elif doraSuit == "z" and doraSrcNum >= 5 and doraSrcNum <= 7:
                    doraNum = (doraSrcNum + 2) % 3 + 5
                # 数牌
                elif doraSuit != "z":
                    if doraSrcNum == 0:
                        doraNum = 6
                    else:
                        doraNum = doraSrcNum % 9 + 1
            else:
                doraNum = 8
                doraSuit = "z"
        # 現ドラをドラとして表示するとき
        else:
            if suits.find(doraSuit) != -1 and numbers.find(str(doraSrcNum)) != -1:
                doraNum = doraSrcNum
                doraSuit = doraSuit
            else:
                doraNum = 8
                doraSuit = "z"

        return doraSrcNum,doraNum,doraSuit


        #文字列を行構成パーツとして返す
    def stringToParts(self,st,fntSize,paiWidth,paiHeight,paifix_x,paifix_y,interval,additionalInterval,start_x,start_y,margin,defaultStroke,doraStr = ""):

        margin = self.fixScale(margin)
        fnt = ImageFont.truetype(self.stFontName,self.fixScale(fntSize))
        drawPartsList = []

        nTotalRow = 0
        nTotalWidth = 0

        #1文字ずつ処理
        for count,char in enumerate(st):
            
            nCurrentRow = 0
            nCurrentPosX = 0
            nCurrentPosY = 0
            nCurrentWidth = 0
            nCurrentCond = 0
            stCurrent = ""
            bIsPai = False
            bIsReturn = (charForNewLine.find(char) != -1)

            #数字ならば、牌であるかどうかチェック
            if numbers.find(char) != -1 and count != len(st)-1:
                for i in range(count+1,len(st)):
                    if suits.find(st[i:i+1]) != -1:
                        stCurrent = st[count:count+1] + st[i:i+1]
                        nCurrentWidth = self.fixScale(paiWidth)
                        bIsPai = True
                        for x in range(i+1,len(st)):
                            if funcs.find(st[x:x+1]) == 0: #リーチ
                                nCurrentWidth = self.fixScale(paiHeight)
                                nCurrentCond += 1
                            elif funcs.find(st[x:x+1]) == 1: #ツモ切
                                nCurrentCond += 2
                            elif funcs.find(st[x:x+1]) == 2: #鳴き手出し
                                nCurrentCond += 4
                            elif funcs.find(st[x:x+1]) == 3: #副露
                                nCurrentWidth = self.fixScale(paiHeight)
                                nCurrentCond += 8
                            else:
                                break

                        break
                    elif numbers.find(st[i:i+1]) != -1:
                        continue
                    else:
                        break

            #特殊記号ならば、直前の一文字がmpszか特殊記号ならば空文字列
            if funcs.find(char) != -1 and count > 0 and \
                (suits.find(st[count-1]) != -1 or funcs.find(st[count-1]) != -1):
                continue
            #mpszならば、直前の一文字が数字ならば空文字列
            elif suits.find(char) != -1 and count > 0 and \
                numbers.find(st[count-1]) != -1:
                continue
            #改行文字
            elif bIsReturn:
                nCurrentWidth = self.nPicWidth
                stCurrent = ""
                bIsPai = False
            #ただの文字
            elif not bIsPai:
                imgZeros = np.zeros((self.nPicWidth,self.nPicWidth),np.uint8)
                imgZeros = Image.fromarray(imgZeros)
                drSentenceDraw = ImageDraw.Draw(imgZeros)
                w = drSentenceDraw.textsize(char,fnt)[0]
                nCurrentWidth = w
                stCurrent = char
                bIsPai = False

            bOverWidth = nTotalWidth + nCurrentWidth > self.nPicWidth - (margin*2)
            if not bOverWidth:
                nCurrentRow = nTotalRow
                nCurrentPosX = nTotalWidth + margin
                nTotalWidth += nCurrentWidth
            elif bIsReturn:
                nCurrentRow = nTotalRow + 1
                nCurrentPosX = margin
                nTotalWidth = 0
                nTotalRow += 1
            else:
                nCurrentRow = nTotalRow + 1
                nCurrentPosX = margin
                nTotalWidth = nCurrentWidth
                nTotalRow += 1

            if bIsPai:
                nCurrentPosY = nCurrentRow*self.fixScale(additionalInterval) + self.fixScale(start_y-paifix_y+20*nCurrentRow)
                if nCurrentCond == 8:
                    nCurrentPosY = nCurrentRow*self.fixScale(additionalInterval) + self.fixScale(start_y-paifix_y+20*nCurrentRow) + self.fixScale(paiHeight-paiWidth)
            else:
                nCurrentPosY = nCurrentRow*self.fixScale(additionalInterval) + self.fixScale(start_y+20*nCurrentRow)

            bReech = False
            bDarken = False
            bStroke = defaultStroke
            strokeColor = "Gray"
            bCrown = False

            if nCurrentCond == 1 or nCurrentCond == 3 or nCurrentCond == 5 or nCurrentCond == 7 or nCurrentCond == 8: #リーチ
                bReech = True

            if nCurrentCond == 2 or nCurrentCond == 3 or nCurrentCond == 6 or nCurrentCond == 7: #ツモ切
                bDarken = True

            if nCurrentCond == 4 or nCurrentCond == 5 or nCurrentCond == 6 or nCurrentCond == 7: #鳴き手出し
                bStroke = True
                strokeColor = "Red"
                
            if doraStr != "":
                if doraStr == stCurrent:
                    bCrown = True
                elif stCurrent == "0m" or stCurrent == "0p" or stCurrent == "0s":
                    bCrown = True

            drawPartsList.append(draw_parts(self.fixScale(nCurrentWidth),stCurrent,bIsPai,nCurrentRow,nCurrentPosX,nCurrentPosY,bReech,bCrown,bDarken,bStroke,strokeColor))

        return drawPartsList

    def getMaxRowOfParts(self,partsList):
        n = 0
        for prt in partsList:
            n = prt.row

        return n

    def hasNakiTedashi(self,partsList):
        for prt in partsList:
            if prt.strokeColor == "Red":
                return True
        return False

    #文字と牌データを描画する
    def drawPartsToImg(self,imBase,prtList,paiSizeX,paiSizeY,fntSize,maxRow,rot):

        #for pt in prtList:
        #    print(str(pt.width) + " / " + pt.contents + " / " + str(pt.isPai) + " / " + str(pt.row) + " / " + str(pt.posX) + " / " + str(pt.posY))
        fnt = ImageFont.truetype(self.stFontName,self.fixScale(fntSize))
        imCurrent = Image.new('RGBA',imBase.size,(0,0,0,0))

        for prt in prtList:
            if prt.row >= maxRow:
                break

            if prt.isPai == True:
                imInsertPai = Image.open(stPaigaFolderPath + prt.contents + ".png").convert("RGBA")
                imInsertPai = imInsertPai.resize(size=(self.fixScale(paiSizeX),self.fixScale(paiSizeY)))

                if prt.darken == True:
                    imgBlack = Image.new('RGBA',imInsertPai.size,(0,0,0,50))
                    imInsertPai.paste(imgBlack,(0,0),imgBlack)

                if(prt.strokeOn == True):
                    imStroke = Image.open(stStrokePath[0]).convert("RGBA")
                    im = np.array(imStroke)
                    #色の処理 pythonはBGR
                    if prt.strokeColor == "Gray":
                        imStroke = im.copy()
                        imStroke[:,:,2] = 0
                        imStroke[:,:,1] = 0
                        imStroke[:,:,0] = 0
                        imStroke = Image.fromarray(np.uint8(imStroke))
                    elif prt.strokeColor == "Red":
                        imStroke = Image.open(stStrokePath[1]).convert("RGBA")
                        im = np.array(imStroke)
                        imStroke = im.copy()
                        imStroke[:,:,(1,2)] = 0
                        imStroke = Image.fromarray(np.uint8(imStroke))
                    elif prt.strokeColor == "Green":
                        imStroke = im.copy()
                        imStroke[:,:,(0,2)] = 0
                        imStroke = Image.fromarray(np.uint8(imStroke))
                    elif prt.strokeColor == "Blue":
                        imStroke = im.copy()
                        imStroke[:,:,(0,1)] = 0
                        imStroke = Image.fromarray(np.uint8(imStroke))

                    imStroke = imStroke.resize(size=(self.fixScale(paiSizeX),self.fixScale(paiSizeY)))
                    imInsertPai.paste(imStroke,(0,0),imStroke)

                imInsertPai = imInsertPai.rotate(prt.rot,expand = True)
                imCurrent.paste(imInsertPai,(prt.posX,prt.posY),imInsertPai)
                
                if prt.crownOn == True:
                    imCrown = Image.open(stCrownPath)
                    imCrown = imCrown.resize(size=(self.fixScale(paiSizeX),self.fixScale(paiSizeX)))
                    imCurrent.paste(imCrown,(prt.posX,prt.posY-self.fixScale(paiSizeX)),imCrown)



            else:
                #draw.text((prt.posX,prt.posY),prt.contents,font=fnt,fill=(0,0,0,255))
                ImageDraw.Draw(imCurrent).text((prt.posX,prt.posY),prt.contents,font=fnt,fill=(0,0,0,255))
                pass

        if rot != 0:
            imCurrent = imCurrent.rotate(rot,expand = True)

        imBase.paste(imCurrent,(0,0),imCurrent)

        
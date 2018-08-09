  # -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 09:38:25 2018
@author: yangyanhao
"""

###############################################################################
################## Python使用PIL库识别条形码及其可译码度的研究与探讨 #############
###############################################################################


##################### 一、视觉信息转化为数据 ####################################

############################# 例子 ############################################
'''
newImg = Image.new("RGB",(2,2))
newImg.putpixel((0,0),(255,255,0))
newImg.putpixel((0,1),(255,0,0))
newImg.putpixel((1,0),(0,255,0))
newImg.putpixel((1,1),(255,255,255))
print(newImgL.getpixel((0,0)),
      newImgL.getpixel((0,1)),
      newImgL.getpixel((1,0)),
      newImgL.getpixel((1,1))
      )
'''

from PIL import Image
img_add=input('请输入图片地址(如 EAN-13.jpg)：')
img = Image.open(img_add)  
img=img.convert('1')    # 转为模式“1”

##################### 二、获取色块宽度（单位：像素） ############################

def block_Width(img,axis_y):
    A = img.load()
    if axis_y in range(1,10):
        height=int(img.size[1]/10*axis_y)
        ss = []
        for x in range(img.size[0]):  
            ss.append(str(A[x, height]))
        ls = [1]
        for i in range(len(ss)-1):
            if(ss[i]==ss[i+1]):
                ls[-1]+=1
            else:
                ls.append(1)
        return(ls)
    else:
        print('输入错误')

axis_y=int(input('请输入初始高度，范围1-9：'))
width=block_Width(img,axis_y)
########################### 三、识别出条码位置 #################################

def find_barcode(width):
    bar=[]
    i=0
    while (int(width[i]/width[i+1])!=1 and  # 起始符
           int(width[i]/width[i+2])!=1 and
           int(width[i]/width[i+27])!=1 and # 间隔符
           int(width[i]/width[i+28])!=1 and
           int(width[i]/width[i+29])!=1 and
           int(width[i]/width[i+30])!=1 and
           int(width[i]/width[i+31])!=1 and
           int(width[i]/width[i+56])!=1 and # 终止符
           int(width[i]/width[i+57])!=1 and
           int(width[i]/width[i+58])!=1
           ):
        i+=1
        bar=width[i:(i+59)]
    return(bar)

bar=find_barcode(width)

########################### 四、条码数据处理 ###################################

# GB/T18348附录E内容,计算参数项：
def barcode_parameter(ls):
    barcode=ls[3:27]+ls[32:57]
    dict={}
    split=[]
    for i in range(0,int(len(barcode)),4):  #前6位按A,B字符集
        split.append(barcode[i:(i+4)])
    for i in range(0,6):
        p=sum(split[i][:])      # 条码字符宽度（p）；
        e1=sum(split[i][2:4])   # 相似边缘之间的距离（ei）；
        e2=sum(split[i][1:3])
        b1=split[i][3]
        b2=split[i][1]
        RT1=float((1.5)/7*p)    # 参考阈值（RT)；
        RT2=float((2.5)/7*p)
        RT3=float((3.5)/7*p)
        RT4=float((4.5)/7*p)
        #RT5=float((5.5)/7*p)
        if e1>=RT1 and e1<RT2:  # 条码字符的相似边缘尺寸所包含的模块宽度数（Ei）
            E1=2
        elif e1>=RT2 and e1<RT3:
            E1=3
        elif e1>=RT3 and e1<RT4:
            E1=4
        else:
            E1=5
        
        if e2>=RT1 and e2<RT2:
            E2=2
        elif e1>=RT2 and e2<RT3:
            E2=3
        elif e2>=RT3 and e2<RT4:
            E2=4
        else:
            E2=5
        dict[i]=[E1,E2,e1,e2,b1,b2,p]
    
    for i in range(6,12):   # 后6位按C字符集（实际B、C字符集内容相似）
        p=sum(split[i][:])
        e2=sum(split[i][1:3])
        e1=sum(split[i][0:2])
        b1=split[i][0]
        b2=split[i][2]
        RT1=float((1.5)/7*p)
        RT2=float((2.5)/7*p)
        RT3=float((3.5)/7*p)
        RT4=float((4.5)/7*p)
        #RT5=float((5.5)/7*p)
        if e1>=RT1 and e1<RT2:
            E1=2
        elif e1>=RT2 and e1<RT3:
            E1=3
        elif e1>=RT3 and e1<RT4:
            E1=4
        else:
            E1=5

        if e2>=RT1 and e2<RT2:
            E2=2
        elif e1>=RT2 and e2<RT3:
            E2=3
        elif e2>=RT3 and e2<RT4:
            E2=4
        else:
            E2=5
        dict[i]=[E1,E2,e1,e2,b1,b2,p]
    return(dict)
    
EAN13_Set={"AAAAAA":"0",    # GB12904 5.3.2.3.1
           "AABABB":"1",    # 创建字符集--->前置码 字典
           "AABBAB":"2",
           "AABBBA":"3",
           "ABAABB":"4",
           "ABBAAB":"5",
           "ABBBAA":"6",
           "ABABAB":"7",
           "ABABBA":"8",
           "ABBABA":"9"
               }

EAN13_dictAB={'2,3':'0,A',  # GB12904附录E表E.1内容
              '2,5':'3,A',  # 创建 E1,E2-->译码,字符集字典(0,3,4,5,6,9)
              '5,4':'4,A',
              '4,5':'5,A',
              '5,2':'6,A',
              '3,2':'9,A',
              '5,3':'0,B',
              '5,5':'3,B',
              '2,4':'4,B',
              '3,5':'5,B',
              '2,2':'6,B',
              '4,2':'9,B',
              }
EAN13_dictC={"5,3":'0,C',
             "5,5":'3,C',
             "2,4":'4,C',
             "3,5":'5,C',
             "2,2":'6,C',
             "4,2":'9,C',
             }

def classification1278(E1,E2,e1,e2,b1,b2,p):   # “1、2、7、8”字符的分类判断。
    if E1==3 and E2==4:
        if 7*(b1+b2)/p<=4:
            Numb_set='1,A'
        else:    
            Numb_set='7,A'
    elif E1==4 and E2==3:
        if 7*(b1+b2)/p<=4:
            Numb_set='2,A'
        else:    
            Numb_set='8,A'
    elif E1==4 and E2==4:
        if 7*(b1+b2)/p>3:
            Numb_set='1,B'
        else:    
            Numb_set='7,B'
    elif E1==3 and E2==3:
        if 7*(b1+b2)/p>3:
            Numb_set='2,B'
        else:    
            Numb_set='8,B'
    return(Numb_set)

############################################# 五、条码译码  ########################################################

y=barcode_parameter(bar)
xy=[]   # 译码（1-9）,字符集（ABC）的list
for i in range(12):
    if (y[i][0]==3 and y[i][1]==4) or (y[i][0]==4 and y[i][1]==3) or (y[i][0]==4 and y[i][1]==4) or (y[i][0]==3 and y[i][1]==3):
        xy.append(classification1278(E1=y[i][0],E2=y[i][1],e1=y[i][2],e2=y[i][3],b1=y[i][4],b2=y[i][5],p=y[i][6]))
    else:
        xy.append(EAN13_dictAB[str(y[i][0])+','+str(y[i][1])])
set=[]      # A、B、C字符集list
decode=[]   # 译码0-9除前置码
for i in range(len(xy)):
        decode.append(xy[i][0])
        set.append(xy[i][2])
print('条码译码：',EAN13_Set[''.join(set[0:6])]+''.join(decode))

############################################ 六、可译码度的检测 #######################################################
#18348-2008 附录C 可译码度的测定

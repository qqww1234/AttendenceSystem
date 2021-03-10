
import wx
import wx.grid
import sqlite3
from time import localtime,strftime
import os
from skimage import io as iio
import io
import zlib
import dlib  # 人脸识别的库dlib
import numpy as np  # 数据处理的库numpy
import cv2  # 图像处理的库OpenCv
import _thread
import threading
import xlwt
import win32com.client

ID_NEW_REGISTER = 160           #新建录入
ID_FINISH_REGISTER = 161        #结束录入

ID_START_PUNCHCARD = 190        #开始签到
ID_END_PUNCARD = 191            #结束签到

ID_OPEN_LOGCAT = 283            #打开记录
ID_CLOSE_LOGCAT = 284           #关闭记录
ID_out_logcat=285               #导出数据

ID_Clearn_Date = 65             #清除表格数据
ID_Clearn_Face_Date = 66        #清除人脸数据

ID_WORKER_UNAVIABLE = -1

PATH_FACE = "data/face_img_database/"           #图像保存地址
# face recognition model, the object maps human faces into 128D vectors
facerec = dlib.face_recognition_model_v1("model/dlib_face_recognition_resnet_model_v1.dat")         # Dlib 预测器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('model/shape_predictor_68_face_landmarks.dat')                     #生成面部识别器
def return_euclidean_distance(feature_1, feature_2):                                                #返回欧氏距离
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))            #计算欧氏距离
    print("欧式距离: ", dist)
    if dist > 0.4:          #阈值设为0.4
        return "diff"
    else:
        return "same"

class WAS(wx.Frame):            #外端设计
    def __init__(self):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        wx.Frame.__init__(self,parent=None,title="学生课堂考勤系统",size =(1100,700))

        self.initMenu()
        self.initInfoText()
        self.initGallery()
        self.initDatabase()
        self.initData()

    def initData(self):
        self.name = ""
        self.id =ID_WORKER_UNAVIABLE
        self.face_feature = ""
        self.pic_num = 0
        self.flag_registed = False
        self.puncard_time = "21:00:00"
        self.loadDataBase(1)

    def initMenu(self):

        menuBar = wx.MenuBar()  #生成菜单栏
        menu_Font = wx.Font()#Font(faceName="consolas",pointsize=20)
        menu_Font.SetPointSize(14)
        menu_Font.SetWeight(wx.BOLD)


        registerMenu = wx.Menu() #生成菜单
        self.new_register = wx.MenuItem(registerMenu,ID_NEW_REGISTER,"信息录入")            #菜单栏设置

        self.new_register.SetTextColour("SLATE BLACK")                     
        self.new_register.SetFont(menu_Font)
        registerMenu.Append(self.new_register)

        self.finish_register = wx.MenuItem(registerMenu,ID_FINISH_REGISTER,"完成录入")

        self.finish_register.SetTextColour("SLATE BLACK")
        self.finish_register.SetFont(menu_Font)
        self.finish_register.Enable(False)
        registerMenu.Append(self.finish_register)


        puncardMenu = wx.Menu()
        self.start_punchcard = wx.MenuItem(puncardMenu,ID_START_PUNCHCARD,"开始签到")
  
        self.start_punchcard.SetTextColour("SLATE BLACK")
        self.start_punchcard.SetFont(menu_Font)
        puncardMenu.Append(self.start_punchcard)

        self.end_puncard = wx.MenuItem(puncardMenu,ID_END_PUNCARD,"结束签到")
   
        self.end_puncard.SetTextColour("SLATE BLACK")
        self.end_puncard.SetFont(menu_Font)
        self.end_puncard.Enable(False)
        puncardMenu.Append(self.end_puncard)

        logcatMenu = wx.Menu()
        self.open_logcat = wx.MenuItem(logcatMenu,ID_OPEN_LOGCAT,"打开记录")

        self.open_logcat.SetFont(menu_Font)
        self.open_logcat.SetTextColour("SLATE BLACK")
        logcatMenu.Append(self.open_logcat)

        self.close_logcat = wx.MenuItem(logcatMenu, ID_CLOSE_LOGCAT, "关闭记录")
   
        self.close_logcat.SetFont(menu_Font)
        self.close_logcat.SetTextColour("SLATE BLACK")
        logcatMenu.Append(self.close_logcat)

        self.out_logcat = wx.MenuItem(logcatMenu, ID_out_logcat, "导出数据")
    
        self.out_logcat.SetFont(menu_Font)
        self.out_logcat.SetTextColour("SLATE BLACK")
        logcatMenu.Append(self.out_logcat)

        ClearnMenu = wx.Menu()
        self.Clearn_Date = wx.MenuItem(ClearnMenu,ID_Clearn_Date,"清除表格数据")
  
        self.Clearn_Date.SetFont(menu_Font)
        self.Clearn_Date.SetTextColour("SLATE BLACK")
        ClearnMenu.Append(self.Clearn_Date)

        self.Clearn_Face_Date = wx.MenuItem(ClearnMenu, ID_Clearn_Face_Date, "清除人脸数据")
 
        self.Clearn_Face_Date.SetFont(menu_Font)                          
        self.Clearn_Face_Date.SetTextColour("SLATE BLACK")
        ClearnMenu.Append(self.Clearn_Face_Date)

        menuBar.Append(registerMenu,"&学生信息录入")                                                           #菜单名称
        menuBar.Append(puncardMenu,"&课堂人脸考勤")
        menuBar.Append(logcatMenu,"&考勤记录表")
        menuBar.Append(ClearnMenu,"&数据清除")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,self.OnNewRegisterClicked,id=ID_NEW_REGISTER)                              #菜单方式触发链接
        self.Bind(wx.EVT_MENU,self.OnFinishRegisterClicked,id=ID_FINISH_REGISTER)
        self.Bind(wx.EVT_MENU,self.OnStartPunchCardClicked,id=ID_START_PUNCHCARD)
        self.Bind(wx.EVT_MENU,self.OnEndPunchCardClicked,id=ID_END_PUNCARD)
        self.Bind(wx.EVT_MENU,self.OnOpenLogcatClicked,id=ID_OPEN_LOGCAT)
        self.Bind(wx.EVT_MENU,self.OnCloseLogcatClicked,id=ID_CLOSE_LOGCAT)
        self.Bind(wx.EVT_MENU,self.OnOutLogcatClicked,id=ID_out_logcat)
        self.Bind(wx.EVT_MENU,self.OnClearn_DateClicked,id=ID_Clearn_Date)
        self.Bind(wx.EVT_MENU,self.OnClearn_Face_DateClicked,id=ID_Clearn_Face_Date)


    def OnOutLogcatClicked(self,event):
        self.loadDataBase(2)
                # 创建工作薄
        ws = xlwt.Workbook(encoding='utf-8')
        w = ws.add_sheet(u"签到表")
        w.write(0, 0, u"学号")
        w.write(0, 1, u"姓名")
        w.write(0, 2, u"签到时间")
        for i,id in enumerate(self.logcat_id):
            w.write(i+1, 0, str(id))
            w.write(i+1, 1, self.logcat_name[i])
            w.write(i+1, 2, self.logcat_datetime[i])
        ws.save("qiandao.xls")

        pass


    def OnClearn_DateClicked(self,event):           #删除数据库数据
        self.Clearn_Date.Enable(True)
        self.Clearn_Face_Date.Enable(True)
        self.deletedatabase(2)
        pass


    def OnClearn_Face_DateClicked(self,event):              #删除录入数据
        self.deletedatabase(1)
        pass

    

    def OnOpenLogcatClicked(self,event):
        self.loadDataBase(2)                #加载数据库logcat
        self.SetSize(1100,700)              #必须要变宽才能显示 scrll
        grid = wx.grid.Grid(self,pos=(0,0),size=(1100,560))
        grid.CreateGrid(100, 3)
        for i in range(100):
            for j in range(3):
                grid.SetCellAlignment(i,j,wx.ALIGN_CENTER,wx.ALIGN_CENTER)
        grid.SetColLabelValue(0, "课堂编号")        #第一列标签
        grid.SetColLabelValue(1, "姓名")
        grid.SetColLabelValue(2, "签到时间")
      

        grid.SetColSize(0,250)
        grid.SetColSize(1,250)
        grid.SetColSize(2,350)
        grid.SetCellTextColour("NAVY")
        
        
        for i,id in enumerate(self.logcat_id):
            grid.SetCellValue(i,0,str(id))
            grid.SetCellValue(i,1,self.logcat_name[i])
            grid.SetCellValue(i,2,self.logcat_datetime[i])
 


        pass

    def OnCloseLogcatClicked(self,event):           #关闭记录
        self.SetSize(1100,700)
        self.initGallery()
        pass

    def register_cap(self,event):
        self.cap = cv2.VideoCapture(0)          #创建 cv2 摄像头对象
        self.cap.set(3, 600)            #cap.set(propId, value)
        self.cap.set(4,600)         #设置视频参数，propId设置的视频参数，value设置的参数值


         
        while self.cap.isOpened():          #cap初始化成功
            # cap.read()
            # 返回两个值：
            # 一个布尔值true/false，用来判断读取视频是否成功/是否到视频末尾
            # 图像对象，图像的三维矩阵
            flag, im_rd = self.cap.read()

            kk = cv2.waitKey(1)         #每帧数据延时1ms，延时为0读取的是静态帧
            dets = detector(im_rd, 1)           #人脸数

            if len(dets) != 0:          #检测到人脸
                biggest_face = dets[0]          #取占比最大的脸
                maxArea = 0
                for det in dets:            #绘制矩形框
                    w = det.right() - det.left()
                    h = det.top()-det.bottom()
                    if w*h > maxArea:
                        biggest_face = det
                        maxArea = w*h
                cv2.rectangle(im_rd, tuple([biggest_face.left(), biggest_face.top()]),tuple([biggest_face.right(), biggest_face.bottom()]),(255, 0, 0), 2)
                
                img_height, img_width = im_rd.shape[:2]
                image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
                pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)           #显示图片在窗体上

                cv2.imshow("camera", im_rd)

                # 获取当前捕获到的图像的所有人脸的特征，存储到 features_cap_arr
                shape = predictor(im_rd, biggest_face)
                features_cap = facerec.compute_face_descriptor(im_rd, shape
                
                for i,knew_face_feature in enumerate(self.knew_face_feature):           # 对于某张人脸，遍历所有存储的人脸特征
                    compare = return_euclidean_distance(features_cap, knew_face_feature)            # 将某张人脸与存储的所有人脸数据进行比对
                    if compare == "same":  # 找到了相似脸
                        self.infoText.AppendText("课堂编号:"+str(self.knew_id[i])+" 姓名:"+self.knew_name[i]+" 的人脸数据已存在\r\n")
                        self.flag_registed = True
                        self.OnFinishRegister()
                        _thread.exit()

                face_height = biggest_face.bottom()-biggest_face.top()
                face_width = biggest_face.right()- biggest_face.left()
                im_blank = np.zeros((face_height, face_width, 3), np.uint8)
                try:
                    for ii in range(face_height):
                        for jj in range(face_width):
                            im_blank[ii][jj] = im_rd[biggest_face.top() + ii][biggest_face.left() + jj]
                    if len(self.name)>0:
                        cv2.imencode('.jpg', im_blank)[1].tofile(PATH_FACE + self.name + "/img_face_" + str(self.pic_num) + ".jpg")  # 存储带有中文路径的照片
                        self.pic_num += 1
                        print("写入本地：", str(PATH_FACE + self.name) + "/img_face_" + str(self.pic_num) + ".jpg")
                        self.infoText.AppendText("图片:"+str(PATH_FACE + self.name) + "/img_face_" + str(self.pic_num) + ".jpg保存成功\r\n")
                except:
                    print("保存照片异常,请对准摄像头")

                if  self.new_register.IsEnabled():
                    _thread.exit()
                if self.pic_num == 10:          #拍摄十张照片
                    self.OnFinishRegister()
                    _thread.exit()
                    
    def OnNewRegisterClicked(self,event):           #新建录入
        self.new_register.Enable(False)         #按钮可用标志
        self.finish_register.Enable(True)
        self.loadDataBase(1)            #加载数据库worker_info
        while self.id == ID_WORKER_UNAVIABLE:           #输入信息
            self.id = wx.GetNumberFromUser(message="请输入课堂编号",
                                           prompt="课堂编号", caption="温馨提示",
                                           value=ID_WORKER_UNAVIABLE,
                                           parent=self.bmp,max=1000000000000,min=ID_WORKER_UNAVIABLE)
            for knew_id in self.knew_id:            #信息已存在
                if knew_id == self.id:
                    self.id = ID_WORKER_UNAVIABLE
                    wx.MessageBox(message="编号已存在，请重新输入", caption="警告")

        while self.name == '':
            self.name = wx.GetTextFromUser(message="请输入姓名",
                                           caption="温馨提示",
                                      default_value="", parent=self.bmp)

            for exsit_name in (os.listdir(PATH_FACE)):          #检测是否重名
                if self.name == exsit_name:
                    wx.MessageBox(message="姓名已存在，请重新输入", caption="警告")
                    self.name = ''
                    break
        os.makedirs(PATH_FACE+self.name)
        _thread.start_new_thread(self.register_cap,(event,))
        pass

    def OnFinishRegister(self):         #结束录入

        self.new_register.Enable(True)
        self.finish_register.Enable(False)
        self.cap.release()

        self.bmp.SetBitmap(wx.Bitmap(self.pic_index))
        if self.flag_registed == True:
            dir = PATH_FACE + self.name
            for file in os.listdir(dir):
                os.remove(dir+"/"+file)
                print("已删除已录入人脸的图片", dir+"/"+file)
            os.rmdir(PATH_FACE + self.name)
            print("已删除已录入人脸的姓名文件夹", dir)
            self.initData()
            return
        if self.pic_num>0:
            pics = os.listdir(PATH_FACE + self.name)
            feature_list = []
            feature_average = []
            for i in range(len(pics)):
                pic_path = PATH_FACE + self.name + "/" + pics[i]
                print("正在读的人脸图像：", pic_path)
                img = iio.imread(pic_path)
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                dets = detector(img_gray, 1)
                if len(dets) != 0:
                    shape = predictor(img_gray, dets[0])
                    face_descriptor = facerec.compute_face_descriptor(img_gray, shape)
                    feature_list.append(face_descriptor)
                else:
                    face_descriptor = 0
                    print("未在照片中识别到人脸")
            if len(feature_list) > 0:
                for j in range(128):
                    feature_average.append(0)           #生成多维数组
                    for i in range(len(feature_list)):
                        feature_average[j] += feature_list[i][j]        #生成128D人脸特征向量
                    feature_average[j] = (feature_average[j]) / len(feature_list)                    
                self.insertARow([self.id,self.name,feature_average],1)              #写入数据库worker_info
                self.infoText.AppendText("课堂编号:"+str(self.id)
                                     +" 姓名:"+self.name+" 数据已保存\r\n")
            pass

        else:
            os.rmdir(PATH_FACE + self.name)
            print("已删除空文件夹",PATH_FACE + self.name)
        self.initData()

    def OnFinishRegisterClicked(self,event):
        self.OnFinishRegister()
        pass

    def punchcard_cap(self,event):
        video_capture = cv2.VideoCapture(0)
        #video_capture=cv2.VideoCapture('1.mp4')
        # 语音模块 voice model

        speaker = win32com.client.Dispatch("SAPI.SpVoice")

        name = "Unknown"
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 600)
        self.cap.set(4,600)         #设置视频参数
        while self.cap.isOpened():          #初始化成功
            flag, im_rd = self.cap.read()
            kk = cv2.waitKey(1)         #每帧数据延时1ms
            dets = detector(im_rd, 1)

            if len(dets) != 0:          #检测到人脸
                biggest_face = dets[0]          #取占比最大的脸
                maxArea = 0
                for det in dets:
                    w = det.right() - det.left()
                    h = det.top() - det.bottom()
                    if w * h > maxArea:         #绘制矩形框
                        biggest_face = det
                        maxArea = w * h
                cv2.rectangle(im_rd, tuple([biggest_face.left(), biggest_face.top()]),tuple([biggest_face.right(), biggest_face.bottom()]),(255, 0, 255), 2)
                img_height, img_width = im_rd.shape[:2]
                image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
                pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)           #显示图片
                
                cv2.imshow("camera", im_rd)
                
                shape = predictor(im_rd, biggest_face)          #提取人脸特征
                features_cap = facerec.compute_face_descriptor(im_rd, shape)            #存储人脸特征

                for i, knew_face_feature in enumerate(self.knew_face_feature):          #对于某张人脸，遍历所有存储的人脸特征
                    compare = return_euclidean_distance(features_cap, knew_face_feature)            #将某张人脸与存储的所有人脸数据进行比对
                    if compare == "same":            #找到了相似脸
                        print("same")
                        flag = 0
                        nowdt = self.getDateAndTime()
                        for j,logcat_name in enumerate(self.logcat_name):
                            if logcat_name == self.knew_name[i]  and  nowdt[0:nowdt.index(" ")] == self.logcat_datetime[j][0:self.logcat_datetime[j].index(" ")]:
                                self.infoText.AppendText("课堂编号:"+ str(self.knew_id[i])
                                                 + " 姓名:" + self.knew_name[i] + " 重复签到\r\n")
                                flag = 1
                                break

                        if flag == 1:
                            break

                        

                        self.infoText.AppendText("课堂编号:" + str(self.knew_id[i])
                                                 + " 姓名:" + self.knew_name[i] + " 成功签到\r\n")
                        self.insertARow([self.knew_id[i], self.knew_name[i], nowdt, "是"], 2)

                        speaker.Speak("Hello {}, nice to meet you! ".format(self.knew_name[i]))
                        
                        self.loadDataBase(2)
                        break

                if self.start_punchcard.IsEnabled():
                    self.bmp.SetBitmap(wx.Bitmap(self.pic_index))
                    _thread.exit()

    def OnStartPunchCardClicked(self,event):        #开始签到

        self.start_punchcard.Enable(False)
        self.end_puncard.Enable(True)
        self.loadDataBase(2)
        threading.Thread(target=self.punchcard_cap,args=(event,)).start()   #传递参数的多线程
        pass

    def OnEndPunchCardClicked(self,event):          #结束签到
        self.start_punchcard.Enable(True)
        self.end_puncard.Enable(False)
        pass

    def initInfoText(self):             #文字显示
        resultText = wx.StaticText(parent=self, pos = (10,580),size=(90, 60))
        resultText.SetBackgroundColour('red')

        self.info = "     欢迎来到课堂考勤系统    \r\n"                              #文字设置
        self.infoText = wx.TextCtrl(parent=self,pos=(0,560),size=(1085,140),
                   style=(wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY))           #水平滚动条
        self.infoText.SetForegroundColour("BLACK")
        self.infoText.SetLabel(self.info)
        font = wx.Font()
        font.SetPointSize(12)
        font.SetWeight(wx.BOLD)
        font.SetUnderlined(True)

        self.infoText.SetFont(font)
        self.infoText.SetBackgroundColour('WHITE')
        pass

    def initGallery(self):          #封面设置
        self.pic_index = wx.Image("drawable/index.png", wx.BITMAP_TYPE_ANY).Scale(1100, 560)
        self.bmp = wx.StaticBitmap(parent=self, pos=(0,0), bitmap=wx.Bitmap(self.pic_index))          
        pass

    def getDateAndTime(self):       #得到当前时间
        dateandtime = strftime("%Y-%m-%d %H:%M:%S",localtime())
        return "["+dateandtime+"]" 

    #数据库部分
    
    def initDatabase(self):         #初始化数据库
        conn = sqlite3.connect("inspurer.db")  #建立数据库连接
        cur = conn.cursor()             #得到游标对象
        cur.execute('''create table if not exists worker_info
        (name text not null,
        id int64 not null primary key,
        face_feature array not null)''')
        cur.execute('''create table if not exists logcat
         (datetime text not null,
         id int64 not null,
         name text not null,
         late text not null)''')
        cur.close()
        conn.commit()
        conn.close()

    def adapt_array(self,arr):
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)

        dataa = out.read()          # 压缩数据流
        return sqlite3.Binary(zlib.compress(dataa, zlib.Z_BEST_COMPRESSION))

    def convert_array(self,text):
        out = io.BytesIO(text)
        out.seek(0)

        dataa = out.read()          # 解压缩数据流
        out = io.BytesIO(zlib.decompress(dataa))
        return np.load(out)

    def insertARow(self,Row,type):          #写入数据
        conn = sqlite3.connect("inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象
        if type == 1:           #选择worker_info表
            cur.execute("insert into worker_info (id,name,face_feature) values(?,?,?)",
                    (Row[0],Row[1],self.adapt_array(Row[2])))
            print("写人脸数据成功")
        if type == 2:           #选择logcat表
            cur.execute("insert into logcat (id,name,datetime,late) values(?,?,?,?)",
                        (Row[0],Row[1],Row[2],Row[3]))
            print("写日志成功")
            pass
        cur.close()
        conn.commit()
        conn.close()
        pass

    def loadDataBase(self,type):            #加载数据

        conn = sqlite3.connect("inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象

        if type == 1:           #选择worker_info表
            self.knew_id = []
            self.knew_name = []
            self.knew_face_feature = []
            cur.execute('select id,name,face_feature from worker_info')
            origin = cur.fetchall()
            for row in origin:          #逐行导入数据
                print(row[0])
                self.knew_id.append(row[0])
                print(row[1])
                self.knew_name.append(row[1])
                print(self.convert_array(row[2]))
                self.knew_face_feature.append(self.convert_array(row[2]))
        if type == 2:           #选择logcat表
            self.logcat_id = []
            self.logcat_name = []
            self.logcat_datetime = []
            self.logcat_late = []
            cur.execute('select id,name,datetime,late from logcat')
            origin = cur.fetchall()
            for row in origin:          #逐行导入数据
                print(row[0])
                self.logcat_id.append(row[0])
                print(row[1])
                self.logcat_name.append(row[1])
                print(row[2])
                self.logcat_datetime.append(row[2])
                print(row[3])
                self.logcat_late.append(row[3])
        pass
    def deletedatabase(self,type):          #删除数据库数据
        conn = sqlite3.connect("inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象
        if type==2:         #选择logcat表
            sql = "DELETE FROM logcat WHERE id > '%d'" % (0)
            cur.execute(sql)
            cur.close()
            conn.commit()
            conn.close()
        if type==1:         #选择worker_info表
            sql = "DELETE FROM worker_info WHERE id > '%d'" % (0)
            cur.execute(sql)
            cur.close()
            conn.commit()
            conn.close()
        pass
        
app = wx.App()
frame = WAS()
frame.Show()
app.MainLoop()


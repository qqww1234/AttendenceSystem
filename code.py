#coding=utf-8
import wx
import wx.grid
import sqlite3
from time import localtime,strftime
import os
from skimage import io as iio
import io
import zlib
import dlib  # ����ʶ��Ŀ�dlib
import numpy as np  # ���ݴ���Ŀ�numpy
import cv2  # ͼ����Ŀ�OpenCv
import _thread

ID_NEW_REGISTER = 160
ID_FINISH_REGISTER = 161

ID_START_PUNCHCARD = 190
ID_END_PUNCARD = 191

ID_OPEN_LOGCAT = 283
ID_CLOSE_LOGCAT = 284

ID_WORKER_UNAVIABLE = -1

PATH_FACE = "data/face_img_database/"
# face recognition model, the object maps human faces into 128D vectors
facerec = dlib.face_recognition_model_v1("model/dlib_face_recognition_resnet_model_v1.dat")
# Dlib Ԥ����
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('model/shape_predictor_68_face_landmarks.dat')
def return_euclidean_distance(feature_1, feature_2):
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
    print("ŷʽ����: ", dist)
    if dist > 0.4:
        return "diff"
    else:
        return "same"

class WAS(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent=None,title="Ա������ϵͳ",size=(920,560))

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
        self.puncard_time = "09:00:00"
        self.loadDataBase(1)

    def initMenu(self):

        menuBar = wx.MenuBar()  #���ɲ˵���
        menu_Font = wx.Font()#Font(faceName="consolas",pointsize=20)
        menu_Font.SetPointSize(14)
        menu_Font.SetWeight(wx.BOLD)


        registerMenu = wx.Menu() #���ɲ˵�
        self.new_register = wx.MenuItem(registerMenu,ID_NEW_REGISTER,"�½�¼��")
        self.new_register.SetBitmap(wx.Bitmap("drawable/new_register.png"))
        self.new_register.SetTextColour("SLATE BLUE")
        self.new_register.SetFont(menu_Font)
        registerMenu.Append(self.new_register)

        self.finish_register = wx.MenuItem(registerMenu,ID_FINISH_REGISTER,"���¼��")
        self.finish_register.SetBitmap(wx.Bitmap("drawable/finish_register.png"))
        self.finish_register.SetTextColour("SLATE BLUE")
        self.finish_register.SetFont(menu_Font)
        self.finish_register.Enable(False)
        registerMenu.Append(self.finish_register)


        puncardMenu = wx.Menu()
        self.start_punchcard = wx.MenuItem(puncardMenu,ID_START_PUNCHCARD,"��ʼǩ��")
        self.start_punchcard.SetBitmap(wx.Bitmap("drawable/start_punchcard.png"))
        self.start_punchcard.SetTextColour("SLATE BLUE")
        self.start_punchcard.SetFont(menu_Font)
        puncardMenu.Append(self.start_punchcard)

        self.end_puncard = wx.MenuItem(puncardMenu,ID_END_PUNCARD,"����ǩ��")
        self.end_puncard.SetBitmap(wx.Bitmap("drawable/end_puncard.png"))
        self.end_puncard.SetTextColour("SLATE BLUE")
        self.end_puncard.SetFont(menu_Font)
        self.end_puncard.Enable(False)
        puncardMenu.Append(self.end_puncard)

        logcatMenu = wx.Menu()
        self.open_logcat = wx.MenuItem(logcatMenu,ID_OPEN_LOGCAT,"����־")
        self.open_logcat.SetBitmap(wx.Bitmap("drawable/open_logcat.png"))
        self.open_logcat.SetFont(menu_Font)
        self.open_logcat.SetTextColour("SLATE BLUE")
        logcatMenu.Append(self.open_logcat)

        self.close_logcat = wx.MenuItem(logcatMenu, ID_CLOSE_LOGCAT, "�ر���־")
        self.close_logcat.SetBitmap(wx.Bitmap("drawable/close_logcat.png"))
        self.close_logcat.SetFont(menu_Font)
        self.close_logcat.SetTextColour("SLATE BLUE")
        logcatMenu.Append(self.close_logcat)

        menuBar.Append(registerMenu,"&����¼��")
        menuBar.Append(puncardMenu,"&ˢ��ǩ��")
        menuBar.Append(logcatMenu,"&������־")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,self.OnNewRegisterClicked,id=ID_NEW_REGISTER)
        self.Bind(wx.EVT_MENU,self.OnFinishRegisterClicked,id=ID_FINISH_REGISTER)
        self.Bind(wx.EVT_MENU,self.OnStartPunchCardClicked,id=ID_START_PUNCHCARD)
        self.Bind(wx.EVT_MENU,self.OnEndPunchCardClicked,id=ID_END_PUNCARD)
        self.Bind(wx.EVT_MENU,self.OnOpenLogcatClicked,id=ID_OPEN_LOGCAT)
        self.Bind(wx.EVT_MENU,self.OnCloseLogcatClicked,id=ID_CLOSE_LOGCAT)

    def OnOpenLogcatClicked(self,event):
        self.loadDataBase(2)
        grid = wx.grid.Grid(self,pos=(320,0),size=(600,500))
        grid.CreateGrid(100, 4)
        for i in range(100):
            for j in range(4):
                grid.SetCellAlignment(i,j,wx.ALIGN_CENTER,wx.ALIGN_CENTER)
        grid.SetColLabelValue(0, "����") #��һ�б�ǩ
        grid.SetColLabelValue(1, "����")
        grid.SetColLabelValue(2, "��ʱ��")
        grid.SetColLabelValue(3, "�Ƿ�ٵ�")

        grid.SetColSize(0,100)
        grid.SetColSize(1,100)
        grid.SetColSize(2,150)
        grid.SetColSize(3,150)


        grid.SetCellTextColour("NAVY")
        for i,id in enumerate(self.logcat_id):
            grid.SetCellValue(i,0,str(id))
            grid.SetCellValue(i,1,self.logcat_name[i])
            grid.SetCellValue(i,2,self.logcat_datetime[i])
            grid.SetCellValue(i,3,self.logcat_late[i])

        pass

    def OnCloseLogcatClicked(self,event):
        self.initGallery()
        pass

    def register_cap(self,event):
        # ���� cv2 ����ͷ����
        self.cap = cv2.VideoCapture(0)
        # cap.set(propId, value)
        # ������Ƶ������propId���õ���Ƶ������value���õĲ���ֵ
        # self.cap.set(3, 600)
        # self.cap.set(4,600)
        # cap�Ƿ��ʼ���ɹ�
        while self.cap.isOpened():
            # cap.read()
            # ��������ֵ��
            #    һ������ֵtrue/false�������ж϶�ȡ��Ƶ�Ƿ�ɹ�/�Ƿ���Ƶĩβ
            #    ͼ�����ͼ�����ά����
            flag, im_rd = self.cap.read()

            # ÿ֡������ʱ1ms����ʱΪ0��ȡ���Ǿ�̬֡
            kk = cv2.waitKey(1)
            # ������ dets
            dets = detector(im_rd, 1)

            # ��⵽����
            if len(dets) != 0:
                biggest_face = dets[0]
                #ȡռ��������
                maxArea = 0
                for det in dets:
                    w = det.right() - det.left()
                    h = det.top()-det.bottom()
                    if w*h > maxArea:
                        biggest_face = det
                        maxArea = w*h
                        # ���ƾ��ο�

                cv2.rectangle(im_rd, tuple([biggest_face.left(), biggest_face.top()]),
                                      tuple([biggest_face.right(), biggest_face.bottom()]),
                                      (255, 0, 0), 2)
                img_height, img_width = im_rd.shape[:2]
                image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
                pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
                # ��ʾͼƬ��panel��
                self.bmp.SetBitmap(pic)

                # ��ȡ��ǰ���񵽵�ͼ��������������������洢�� features_cap_arr
                shape = predictor(im_rd, biggest_face)
                features_cap = facerec.compute_face_descriptor(im_rd, shape)

                # ����ĳ���������������д洢����������
                for i,knew_face_feature in enumerate(self.knew_face_feature):
                    # ��ĳ��������洢�������������ݽ��бȶ�
                    compare = return_euclidean_distance(features_cap, knew_face_feature)
                    if compare == "same":  # �ҵ���������
                        self.infoText.AppendText(self.getDateAndTime()+"����:"+str(self.knew_id[i])
                                                 +" ����:"+self.knew_name[i]+" �����������Ѵ���\r\n")
                        self.flag_registed = True
                        self.OnFinishRegister()
                        _thread.exit()

                        # print(features_known_arr[i][-1])
                face_height = biggest_face.bottom()-biggest_face.top()
                face_width = biggest_face.right()- biggest_face.left()
                im_blank = np.zeros((face_height, face_width, 3), np.uint8)
                try:
                    for ii in range(face_height):
                        for jj in range(face_width):
                            im_blank[ii][jj] = im_rd[biggest_face.top() + ii][biggest_face.left() + jj]
                    # cv2.imwrite(path_make_dir+self.name + "/img_face_" + str(self.sc_number) + ".jpg", im_blank)
                    # cap = cv2.VideoCapture("***.mp4")
                    # cap.set(cv2.CAP_PROP_POS_FRAMES, 2)
                    # ret, frame = cap.read()
                    # cv2.imwrite("��//h.jpg", frame)  # �÷������ɹ�
                    # ���python3��ʹ��cv2.imwrite�洢��������·��ͼƬ
                    if len(self.name)>0:
                        cv2.imencode('.jpg', im_blank)[1].tofile(
                        PATH_FACE + self.name + "/img_face_" + str(self.pic_num) + ".jpg")  # ��ȷ����
                        self.pic_num += 1
                        print("д�뱾�أ�", str(PATH_FACE + self.name) + "/img_face_" + str(self.pic_num) + ".jpg")
                        self.infoText.AppendText(self.getDateAndTime()+"ͼƬ:"+str(PATH_FACE + self.name) + "/img_face_" + str(self.pic_num) + ".jpg����ɹ�\r\n")
                except:
                    print("������Ƭ�쳣,���׼����ͷ")

                if  self.new_register.IsEnabled():
                    _thread.exit()
                if self.pic_num == 10:
                    self.OnFinishRegister()
                    _thread.exit()
    def OnNewRegisterClicked(self,event):
        self.new_register.Enable(False)
        self.finish_register.Enable(True)
        self.loadDataBase(1)
        while self.id == ID_WORKER_UNAVIABLE:
            self.id = wx.GetNumberFromUser(message="���������Ĺ���(-1������)",
                                           prompt="����", caption="��ܰ��ʾ",
                                           value=ID_WORKER_UNAVIABLE,
                                           parent=self.bmp,max=100000000,min=ID_WORKER_UNAVIABLE)
            for knew_id in self.knew_id:
                if knew_id == self.id:
                    self.id = ID_WORKER_UNAVIABLE
                    wx.MessageBox(message="�����Ѵ��ڣ�����������", caption="����")

        while self.name == '':
            self.name = wx.GetTextFromUser(message="���������ĵ�����,���ڴ��������ļ���",
                                           caption="��ܰ��ʾ",
                                      default_value="", parent=self.bmp)

            # ����Ƿ�����
            for exsit_name in (os.listdir(PATH_FACE)):
                if self.name == exsit_name:
                    wx.MessageBox(message="�����ļ����Ѵ��ڣ�����������", caption="����")
                    self.name = ''
                    break
        os.makedirs(PATH_FACE+self.name)
        _thread.start_new_thread(self.register_cap,(event,))
        pass

    def OnFinishRegister(self):
        self.new_register.Enable(True)
        self.finish_register.Enable(False)
        self.cap.release()
        self.bmp.SetBitmap(wx.Bitmap(self.pic_index))
        if self.flag_registed == True:
            dir = PATH_FACE + self.name
            for file in os.listdir(dir):
                os.remove(dir+"/"+file)
                print("��ɾ����¼��������ͼƬ", dir+"/"+file)
            os.rmdir(PATH_FACE + self.name)
            print("��ɾ����¼�������������ļ���", dir)
            self.initData()
            return
        if self.pic_num>0:
            pics = os.listdir(PATH_FACE + self.name)
            feature_list = []
            feature_average = []
            for i in range(len(pics)):
                pic_path = PATH_FACE + self.name + "/" + pics[i]
                print("���ڶ�������ͼ��", pic_path)
                img = iio.imread(pic_path)
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                dets = detector(img_gray, 1)
                if len(dets) != 0:
                    shape = predictor(img_gray, dets[0])
                    face_descriptor = facerec.compute_face_descriptor(img_gray, shape)
                    feature_list.append(face_descriptor)
                else:
                    face_descriptor = 0
                    print("δ����Ƭ��ʶ������")
            if len(feature_list) > 0:
                for j in range(128):
                    #��ֹԽ��
                    feature_average.append(0)
                    for i in range(len(feature_list)):
                        feature_average[j] += feature_list[i][j]
                    feature_average[j] = (feature_average[j]) / len(feature_list)
                self.insertARow([self.id,self.name,feature_average],1)
                self.infoText.AppendText(self.getDateAndTime()+"����:"+str(self.id)
                                     +" ����:"+self.name+" �����������ѳɹ�����\r\n")
            pass

        else:
            os.rmdir(PATH_FACE + self.name)
            print("��ɾ�����ļ���",PATH_FACE + self.name)
        self.initData()

    def OnFinishRegisterClicked(self,event):
        self.OnFinishRegister()
        pass

    def punchcard_cap(self,event):
        self.cap = cv2.VideoCapture(0)
        # cap.set(propId, value)
        # ������Ƶ������propId���õ���Ƶ������value���õĲ���ֵ
        # self.cap.set(3, 600)
        # self.cap.set(4,600)
        # cap�Ƿ��ʼ���ɹ�
        while self.cap.isOpened():
            # cap.read()
            # ��������ֵ��
            #    һ������ֵtrue/false�������ж϶�ȡ��Ƶ�Ƿ�ɹ�/�Ƿ���Ƶĩβ
            #    ͼ�����ͼ�����ά����
            flag, im_rd = self.cap.read()
            # ÿ֡������ʱ1ms����ʱΪ0��ȡ���Ǿ�̬֡
            kk = cv2.waitKey(1)
            # ������ dets
            dets = detector(im_rd, 1)

            # ��⵽����
            if len(dets) != 0:
                biggest_face = dets[0]
                # ȡռ��������
                maxArea = 0
                for det in dets:
                    w = det.right() - det.left()
                    h = det.top() - det.bottom()
                    if w * h > maxArea:
                        biggest_face = det
                        maxArea = w * h
                        # ���ƾ��ο�

                cv2.rectangle(im_rd, tuple([biggest_face.left(), biggest_face.top()]),
                              tuple([biggest_face.right(), biggest_face.bottom()]),
                              (255, 0, 255), 2)
                img_height, img_width = im_rd.shape[:2]
                image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
                pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
                # ��ʾͼƬ��panel��
                self.bmp.SetBitmap(pic)

                # ��ȡ��ǰ���񵽵�ͼ��������������������洢�� features_cap_arr
                shape = predictor(im_rd, biggest_face)
                features_cap = facerec.compute_face_descriptor(im_rd, shape)

                # ����ĳ���������������д洢����������
                for i, knew_face_feature in enumerate(self.knew_face_feature):
                    # ��ĳ��������洢�������������ݽ��бȶ�
                    compare = return_euclidean_distance(features_cap, knew_face_feature)
                    if compare == "same":  # �ҵ���������
                        print("same")
                        flag = 0
                        nowdt = self.getDateAndTime()
                        for j,logcat_name in enumerate(self.logcat_name):
                            if logcat_name == self.knew_name[i]  and  nowdt[0:nowdt.index(" ")] == self.logcat_datetime[j][0:self.logcat_datetime[j].index(" ")]:
                                self.infoText.AppendText(nowdt+"����:"+ str(self.knew_id[i])
                                                 + " ����:" + self.knew_name[i] + " ǩ��ʧ��,�ظ�ǩ��\r\n")
                                flag = 1
                                break

                        if flag == 1:
                            break

                        if nowdt[nowdt.index(" ")+1:-1] <= self.puncard_time:
                            self.infoText.AppendText(nowdt + "����:" + str(self.knew_id[i])
                                                 + " ����:" + self.knew_name[i] + " �ɹ�ǩ��,��δ�ٵ�\r\n")
                            self.insertARow([self.knew_id[i],self.knew_name[i],nowdt,"��"],1)
                        else:
                            self.infoText.AppendText(nowdt + "����:" + str(self.knew_id[i])
                                                     + " ����:" + self.knew_name[i] + " �ɹ�ǩ��,���ٵ���\r\n")
                            self.insertARow([self.knew_id[i], self.knew_name[i], nowdt, "��"], 2)
                        self.loadDataBase(2)
                        break

                if self.start_punchcard.IsEnabled():
                    self.bmp.SetBitmap(wx.Bitmap(self.pic_index))
                    _thread.exit()

    def OnStartPunchCardClicked(self,event):
        # cur_hour = datetime.datetime.now().hour
        # print(cur_hour)
        # if cur_hour>=8 or cur_hour<6:
        #     wx.MessageBox(message='''������˽����ǩ��ʱ�䣬����������\n
        #     ÿ���ǩ��ʱ����:6:00~7:59''', caption="����")
        #     return
        self.start_punchcard.Enable(False)
        self.end_puncard.Enable(True)
        self.loadDataBase(2)
        _thread.start_new_thread(self.punchcard_cap,(event,))
        pass

    def OnEndPunchCardClicked(self,event):
        self.start_punchcard.Enable(True)
        self.end_puncard.Enable(False)
        pass

    def initInfoText(self):
        #����������infoText������ɫ����ʧ�ܣ�Ī�����
        resultText = wx.StaticText(parent=self, pos = (10,20),size=(90, 60))
        resultText.SetBackgroundColour('red')

        self.info = "\r\n"+self.getDateAndTime()+"�����ʼ���ɹ�\r\n"
        #�ڶ�������ˮƽ�춯��
        self.infoText = wx.TextCtrl(parent=self,size=(320,500),
                   style=(wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY))
        #ǰ��ɫ��Ҳ����������ɫ
        self.infoText.SetForegroundColour("ORANGE")
        self.infoText.SetLabel(self.info)
        #API:https://www.cnblogs.com/wangjian8888/p/6028777.html
        # û�����������غ������"par is not a key word",ֻ��Set
        font = wx.Font()
        font.SetPointSize(12)
        font.SetWeight(wx.BOLD)
        font.SetUnderlined(True)

        self.infoText.SetFont(font)
        self.infoText.SetBackgroundColour('TURQUOISE')
        pass

    def initGallery(self):
        self.pic_index = wx.Image("drawable/index.png", wx.BITMAP_TYPE_ANY).Scale(600, 500)
        self.bmp = wx.StaticBitmap(parent=self, pos=(320,0), bitmap=wx.Bitmap(self.pic_index))
        pass

    def getDateAndTime(self):
        dateandtime = strftime("%Y-%m-%d %H:%M:%S",localtime())
        return "["+dateandtime+"]"

    #���ݿⲿ��
    #��ʼ�����ݿ�
    def initDatabase(self):
        conn = sqlite3.connect("inspurer.db")  #�������ݿ�����
        cur = conn.cursor()             #�õ��α����
        cur.execute('''create table if not exists worker_info
        (name text not null,
        id int not null primary key,
        face_feature array not null)''')
        cur.execute('''create table if not exists logcat
         (datetime text not null,
         id int not null,
         name text not null,
         late text not null)''')
        cur.close()
        conn.commit()
        conn.close()

    def adapt_array(self,arr):
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)

        dataa = out.read()
        # ѹ��������
        return sqlite3.Binary(zlib.compress(dataa, zlib.Z_BEST_COMPRESSION))

    def convert_array(self,text):
        out = io.BytesIO(text)
        out.seek(0)

        dataa = out.read()
        # ��ѹ��������
        out = io.BytesIO(zlib.decompress(dataa))
        return np.load(out)

    def insertARow(self,Row,type):
        conn = sqlite3.connect("inspurer.db")  # �������ݿ�����
        cur = conn.cursor()  # �õ��α����
        if type == 1:
            cur.execute("insert into worker_info (id,name,face_feature) values(?,?,?)",
                    (Row[0],Row[1],self.adapt_array(Row[2])))
            print("д�������ݳɹ�")
        if type == 2:
            cur.execute("insert into logcat (id,name,datetime,late) values(?,?,?,?)",
                        (Row[0],Row[1],Row[2],Row[3]))
            print("д��־�ɹ�")
            pass
        cur.close()
        conn.commit()
        conn.close()
        pass

    def loadDataBase(self,type):

        conn = sqlite3.connect("inspurer.db")  # �������ݿ�����
        cur = conn.cursor()  # �õ��α����

        if type == 1:
            self.knew_id = []
            self.knew_name = []
            self.knew_face_feature = []
            cur.execute('select id,name,face_feature from worker_info')
            origin = cur.fetchall()
            for row in origin:
                print(row[0])
                self.knew_id.append(row[0])
                print(row[1])
                self.knew_name.append(row[1])
                print(self.convert_array(row[2]))
                self.knew_face_feature.append(self.convert_array(row[2]))
        if type == 2:
            self.logcat_id = []
            self.logcat_name = []
            self.logcat_datetime = []
            self.logcat_late = []
            cur.execute('select id,name,datetime,late from logcat')
            origin = cur.fetchall()
            for row in origin:
                print(row[0])
                self.logcat_id.append(row[0])
                print(row[1])
                self.logcat_name.append(row[1])
                print(row[2])
                self.logcat_datetime.append(row[2])
                print(row[3])
                self.logcat_late.append(row[3])
        pass
app = wx.App()
frame = WAS()
frame.Show()
app.MainLoop()

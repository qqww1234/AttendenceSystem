from tkinter import *
import tkinter.messagebox
from tkinter import scrolledtext
import cv2
import os
from facerec_from_webcam_faster import *

class App(object):
    def __init__(self, master):
        self.com1 = Button(master, text='信息录入', command=self.capture_camera)
        self.com2 = Button(master, text='人脸检测', command=facerec)
        self.com3 = Button(master, text='数据记录', command=self.read_txt)
        self.l = Label(master, text='输入你的学号: ')
        self.l2 = Label(master, text='摄像头开启后按c拍照按q退出')
        self.e = Entry(master,width=30)

        #self.e.insert('insert', 'Hello Entry')
        #e.delete(0, END)
        #安排按钮位置
        self.t = scrolledtext.ScrolledText(master, height=20)
        self.l.pack(side=TOP)
        self.e.pack(side=TOP)
        self.com1.pack(side=TOP)
        self.l2.pack(side=TOP)
        self.t.pack(side=BOTTOM)
        self.com2.pack(side=TOP)
        self.com3.pack(side=TOP)
        #tkinter.messagebox.showinfo(title='Hi', message='请在第一个文本框输入你的名字')

    def say_hello(self):#测试
        print ('ok')

    #读取face_record并且显示在页面下方
    def read_txt(self):
        fp=open('./dataset/face_record.txt','r')
        alllines = fp.readlines();
        fp.close();
        for eachline in alllines:
            self.t.insert(END,eachline)

    def capture_camera(self):
        """
        下面是从摄像头捕捉实时流,以及采集照片,并将其写入文件的Python实现。
        运行程序后:
        1. 现在命令行输入采集照片人的姓名(拼音),如me
        2. 选中摄像头框,并切换到英文输入法,按键Q推出，按键C 进行拍照并保存到指定的路径,
           此处avi文件保存在当前路径,每个人的照片保存在dataset单独的文件夹中
        3. 当捕获的照片数量大于size(8),重复步骤1
        """
        # Create a VideoCapture object
        #cap = cv2.VideoCapture('1.mp4')
        cap=cv2.VideoCapture(0)
        # Check if camera opened successfully
        if not cap.isOpened():
            print("Unable to read camera feed")
        # Default resolutions of the frame are obtained.The default resolutions are system dependent.
        # We convert the resolutions from float to integer.
        # 默认分辨率取决于系统。
        # 我们将分辨率从float转换为整数。
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
        # 定义编解码器并创建VideoWriter对象。输出存储在“outpy.avi”文件中。
        name = "me"
        image_base_path = "./dataset"
        out = cv2.VideoWriter(image_base_path + '/outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                              (frame_width, frame_height))
        if not os.path.exists(image_base_path):
            os.makedirs(image_base_path)
        index = 0  #
        size = 8  # record 8 different image from different direction
        flag = True


        while True:
            ret, frame = cap.read()
            if ret:
                # Write the frame into the file 'output.avi'
                out.write(frame)
                if flag and index == 0:  # or index % size == 0
                    flag = False
                    name=self.e.get()
                    #name = input("############please input a name and then press enter key to continue ############:")
                # Display the resulting frame
                cv2.imshow('frame', frame)
                key = cv2.waitKey(1)
                # Press Q on keyboard to stop recordingqc
                if key & 0xFF == ord('q'):
                    break
                if key & 0xFF == ord('c'):
                    index += 1
                    if not os.path.exists(image_base_path + "/" + name):
                        os.makedirs(image_base_path + "/" + name)
                    cv2.imwrite("{}/{}/{}_{}.jpg".format(image_base_path, name, name, index), frame)
                    if index == size:
                        tkinter.messagebox.showinfo(title='Hi', message='请重新输入姓名')
                        self.e.delete(0, tkinter.END)
                        break
                        #index = 0
                        #flag = True
            # Break the loop
            else:
                break

        # When everything done, release the video capture and video write objects
        cap.release()
        out.release()
        # Closes all the frames
        cv2.destroyAllWindows()

    # capture_camera()

root = Tk()
root.title('人脸考勤系统')
root.geometry('400x420')

app = App(root)
root.mainloop()


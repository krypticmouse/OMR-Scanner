import os
import cv2
import imutils
import numpy as np
from imutils import contours
from random import choice

options = ['A','B','C','D']
detail_names = ['Enroll.jpeg','1-5.jpeg','6-10.jpeg',
                '11-12.jpeg','13-14.jpeg','15-16.jpeg',
                '17-18.jpeg','19-20.jpeg']

class OMR_Evaluator:
    def __init__(self,path,answer_key):
        self.path = path
        self.answers_key = answer_key
        self.get_details()
        self.enroll = self.get_enroll()
        self.student_answers = self.get_student_answers()
        self.student_score = self.get_score()
    
    def get_score(self):
        correct = 0
        for x,y in zip(self.student_answers, self.answers_key):
            if len(x) == len(y) and len(x) != 0:
                flag = True
                for s_o,a_o in zip(x,y):
                    if s_o != a_o:
                        flag = False
                        break
                if flag:
                    correct += 1
        return correct*5
    
    def get_details(self):
        img = cv2.imread(self.path,0)

        kernel = np.ones((2,2),np.uint8)
        erosion = cv2.erode(img,kernel,iterations = 1)
        edge = cv2.Canny(erosion,255/3,255)

        cnts,_ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[0:3]

        images = []
        for i in list(range(3)):
            x, y, w, h = cv2.boundingRect(cnts[i].astype(np.int))
            crop = img[y:y+h, x:x+w]
            images.append(crop)
        
        if not os.path.isdir('Details'):
            os.makedirs('Details')
        
        img = images[0]
        cv2.imwrite('Details/Enroll.jpeg',img[60:270,5:225])

        img = images[2]
        cv2.imwrite('Details/1-5.jpeg',img[55:250,5:120])
        cv2.imwrite('Details/6-10.jpeg',img[55:250,140:270])

        img = images[1]
        cv2.imwrite('Details/11-12.jpeg',img[5:104,2:120])
        cv2.imwrite('Details/13-14.jpeg',img[5:104,130:260])
        cv2.imwrite('Details/15-16.jpeg',img[5:104,270:400])
        cv2.imwrite('Details/17-18.jpeg',img[5:104,410:540])
        cv2.imwrite('Details/19-20.jpeg',img[5:104,550:680])
        
    def get_student_answers(self):
        bubble = []
        for k in range(1,8):
            upper = 20 if k<3 else 8
            img = cv2.imread('Details/' + detail_names[k])
            
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)[1]

            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            
            questionCnts = sorted(cnts, key=cv2.contourArea, reverse=True)[0:upper]
            questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]

            correct = 0
            color = [(255,0,0),(0,255,0),(0,0,255,),(255,0,255),(255,255,0)]

            for (q, i) in enumerate(np.arange(0, len(questionCnts), 4)):
                cnts = contours.sort_contours(questionCnts[i:i + 4])[0]
                row = []

                for (j, c) in enumerate(cnts):
                    mask = np.zeros(thresh.shape, dtype="uint8")
                    cv2.drawContours(mask, [c], -1, 255, -1)

                    mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                    total = cv2.countNonZero(mask)
                    row.append(total)
                if row[np.argmax(row)] > 170:
                    bubble.append(tuple(np.array(options)[np.where(np.array(row) > 170)]))
                else:
                    bubble.append(tuple())
        return bubble
    
    def get_enroll(self):
        enroll = []
        upper = 100
        img = cv2.imread('Details/' + detail_names[0])
        
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)[1]

        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        
        questionCnts = sorted(cnts, key=cv2.contourArea, reverse=True)[0:upper]
        questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]

        correct = 0
        
        for (q, i) in enumerate(np.arange(0, len(questionCnts), 10)):
            cnts = contours.sort_contours(questionCnts[i:i + 10])[0]
            row = []
            
            for (j, c) in enumerate(cnts):
                mask = np.zeros(thresh.shape, dtype="uint8")
                cv2.drawContours(mask, [c], -1, 255, -1)

                mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                total = cv2.countNonZero(mask)
                row.append(total)            
            enroll.append(row)
        return ''.join(((np.argmax(enroll,axis = 0)+1)%10).astype('str'))
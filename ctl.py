from PyQt5 import QtCore
from bs4 import BeautifulSoup
import requests
import re
import time
import threading
import json

class CtlMacro(QtCore.QObject):
    change_progress = QtCore.pyqtSignal(int, int)
    make_progress = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.mtx = QtCore.QMutex()
        self.cond = QtCore.QWaitCondition()
        self.reloadSession()
        self.init()

    def reloadSession(self):
        self.session = requests.Session()

    def init(self):
        self.currentnum = 0
        self.quitmsg = ""
        self.asp_id = ""
        self.progress = []

    def findlecture(self, id, pwd):
        self.session.get("http://ctl.kduniv.ac.kr/main/MainView.dunet")
        login = self.session.post("http://ctl.kduniv.ac.kr/login/doGetUserCountId.dunet", data={
            "user_id": id,
            "user_password": pwd,
            "is_local" : 'Y',
            "group_cd" : 'UN'
        })
        if login.text.find("alert('비밀번호") != -1:
            j = {}
            j["lock_yn"] = "N"
        else:
            j = json.loads(login.text)
        if "lock_yn" in j and not j["lock_yn"] == "N":
            MainView = self.session.post("http://ctl.kduniv.ac.kr/main/MainView.dunet")
        else:
            success = self.session.get("http://portal.kduniv.ac.kr/c/portal/login", params={"login":id,"password":pwd})
            if not success.text.find("location.replace") == -1: return [False, "login"]
            MainView = self.session.get("http://ctl.kduniv.ac.kr/sso/index.jsp")
        soup = BeautifulSoup(MainView.text, "html.parser")
        lectures = soup(attrs={"class":"lecName"})
        ltinfo = []
        tmps = []
        for lecture in lectures:
            tmp = []
            ltprog = lecture.next_sibling.next_sibling(attrs={"class":"numstate"})[0].text.split("/")
            if ltprog[1] == '0':{}
            elif not ltprog[0] == ltprog[1]:
                tmp.append(lecture("a")[0].text[10:-1])
                for v in lecture("a")[0].attrs["id"].split("_"):
                    tmp.append(v)
                tmps.append(tmp)
        for d in tmps:
            ltdata = self.getlectures(d)
            print(ltdata)
            if len(ltdata["ltdata"]) >= 1:
                ltinfo.append(d)
        if len(ltinfo) < 1: ltinfo = [False, "lecture"]
        return ltinfo

    def getlectures(self, ltinfo):
        baseurl = "http://ctl.kduniv.ac.kr"
        ltdata = []
        #for ltinfo in lectures:
        tmp1 = {}
        ltinfotmp = {}
        url = "/lms/class/classroom/doViewClassRoom_new.dunet"
        data = {
            "mnid" : "201008254671",
        	"course_id" : ltinfo[2],
        	"class_no" : ltinfo[3]
        }
        doViewClassRoom = self.session.post(baseurl + url, data=data)
        soup = BeautifulSoup(doViewClassRoom.text, "html.parser")
        asp_id = soup(attrs={"id":"req_asp_id"})[0].attrs["value"]
        ltlist = soup(attrs={"class":"lenAct_list"})
        ltinfotmp["contents_id"] = ltinfo[2]
        ltinfotmp["class_no"] = ltinfo[3]
        ltinfotmp["asp_id"] = asp_id
        tmp1["ltinfo"] = ltinfotmp
        tmp2 = []
        for lecture in ltlist:
            if lecture("img")[0].attrs["alt"] == "강의":
                ltprog = lecture(attrs={"class":"progressBar"})[0].next_sibling.next_sibling.text[1:]
                if not ltprog == "100%":
                    tmp2.append(lecture(attrs={"class":"lectureWindow"})[0].attrs)
                tmp1["ltdata"] = tmp2
        return tmp1
        #ltdata.append(tmp1)
        #return ltdata

    def test2(self, ltinfo, ltdata):
        baseurl = "http://ctl.kduniv.ac.kr"

        url = "/lms/class/classroom/doViewClassRoom_new.dunet"
        data = {
            "mnid" : "201008254671",
            "course_id" : ltinfo["contents_id"],
            "class_no" : ltinfo["class_no"]
        }
        self.session.post(baseurl + url, data=data)
        url = "/lms/class/lectureWindow/doViewLectureWindow.dunet"
        data = {
            'weekseq_no' : ltdata["weekseq_no"]
            ,'review' : ltdata["review"]
            ,'asp_id' : ltinfo["asp_id"]
            ,'contents_height' : ltdata["window_height"]
            ,'tool_gubun' : ltdata["toolgubun"]
            ,'contents_reg_method' : ltdata["regmethod"]
            ,'study_able_status' : "A"
            ,'contents_id' : ltdata["contents_id"]
            ,'contents_type' : ltdata["contents_type"]
        }
        doViewLectureWindow = self.session.post(baseurl + url, data=data);

        soup = BeautifulSoup(doViewLectureWindow.text, 'html.parser')
        form = soup(attrs={"id":"preForm"})[0]

        url2 = "/lms/class/lectureWindow/doViewWindowPage.dunet"
        data2 = {}
        for input in form("input"):
            data2[input.attrs["id"]]=input.attrs["value"]

        r2 = self.session.post(baseurl + url2, data=data2)

        url3 = "/lms/class/lectureWindow/doUpdateTrackingProgress.dunet"
        data3 = {
            'course_attend_log_no'	:	data2["course_attend_log_no"]
            ,'weekseq_no'			:	data2["weekseq_no"]
            ,'course_id'			:	data2["contents_id"]
            ,'class_no'				:	ltinfo["class_no"]
            ,'asp_id'				:	ltinfo["asp_id"]
            ,'study_time'			:	0
            ,'basic_time'			:	data2["basic_time"]
            ,'progress_check_gubun' :	data2["progress_check_gubun"]
            ,'review'				:	data2["review"]
            ,'study_able_status'    :   data2["study_able_status"]
        }

        self.session.post(baseurl + url3, data=data3)

        p = re.compile('course_study_time = parseInt\(\"([0-9]+)\",10\)');
        m = p.search(r2.text)
        basictime = int(data2["basic_time"])*60+5
        waittime = int(data2["basic_time"])*60 - int(m.group(1))
        starttime = time.time()
        #print(waittime)
        self.mtx.lock()
        a = len(self.progress)
        self.currentnum += 1
        self.progress.append({"basictime":basictime, "waittime":waittime, "starttime":starttime})
        print(data2["weekseq_no"] + ", " + str(self.progress[a]['waittime']))
        try:
            self.cond.wait(self.mtx)
            self.make_progress.emit(a)
        finally:
            self.mtx.unlock()
        while(not self.quitmsg == "q" and time.time() - starttime < waittime + 5):
            #print("{:.2%}".format((((basictime-waittime)+int(time.time() - starttime))/basictime)))
            self.change_progress.emit(a, (basictime-waittime)+int(time.time() - starttime))
            if int(time.time() - starttime) % 300 == 0:
                #print(5)
                self.session.post(baseurl + url3, data=data3)
            time.sleep(1)
        else:
            self.session.post(baseurl + url3, data=data3)
            self.currentnum -= 1
            self.change_progress.emit(a, -1)
            print("end")
            return

    # def keychk(self):
    #     try:
    #         while(not self.quitmsg == "q"):
    #             self.quitmsg = input()
    #     except KeyboardInterrupt: pass
    #     finally: self.quitmsg = "q"

'''if __name__ == '__main__':
    l = findlecture(id, pwd)
    data = getlectures(l[0])
    print(data)
    for d in data:
        quitmsg = ""
        threads = []
        threads.append(threading.Thread(target=keychk))
        for ltdata in d["ltdata"]:
            threads.append(threading.Thread(target=test2, args=(s, d["ltinfo"], ltdata)))

        for t in threads:
            t.start()

        for t in threads:
            t.join()'''

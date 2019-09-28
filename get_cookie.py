import requests,time,re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.ui as ui
import random

class getCookie():
    def __init__(self,driver):
        self.driver=driver

    def get_phone(self):
        timestamp=time.time()
        url=f'http://i.fxhyd.cn:8080/UserInterface.aspx?action=getmobile&token={}&itemid=352&timestamp={timestamp}'
        response=requests.get(url).text
        phone=re.findall("success|(.*)",response,re.S)[1][1:]
        print("自动获取手机号："+phone)

        url='https://h5.ele.me/login/'

        self.driver.get(url=url)
        self.driver.find_element_by_xpath('.//section[@class="MessageLogin-FsPlX"]/input').send_keys(phone)
        self.driver.find_element_by_class_name('CountButton-3e-kd').click()
        #5秒内每隔500毫秒扫描1次页面变化，当出现指定的元素后结束
        wait = ui.WebDriverWait(self.driver,5)
        wait.until(lambda driver: self.driver.find_element_by_xpath('.//span[@id="nc_1_n1z"]'))
        #获取拖拽的模块
        slideblock=self.driver.find_element_by_xpath('.//span[@id="nc_1_n1z"]')
        #鼠标点击不松开
        ActionChains(self.driver).click_and_hold(on_element=slideblock).perform()
        time.sleep(1)
        distance=260
        while distance>0:
            span=random.randint(15,20)
            ActionChains(self.driver).move_by_offset(xoffset=span, yoffset=0).perform()
            distance-=span
            time.sleep(random.randint(10,50)/500)
        #将模块滑至相对起点位置的最右边
        ActionChains(self.driver).move_by_offset(xoffset=distance,yoffset=0).perform()

        ActionChains(self.driver).release(on_element=slideblock).perform()

        aa=self.getMessage(phone)
        return aa

    def getMessage(self,phone):
        response=''
        for i in range(10):
            timestamp=time.time()
            url=f'http://i.fxhyd.cn:8080/UserInterface.aspx?action=getsms&token={}&itemid=352&mobile={phone}&release=1&timestamp={timestamp}'
            time.sleep(3)
            response=requests.get(url).text
            if  "success" in response:
                print(response)
                break

            print(f'第{i+1}次返回错误代码:'+response)
        if "success" not in response:
            self.driver.find_element_by_xpath('.//section[@class="MessageLogin-FsPlX"]/input').clear()
            # driver.close()
            return self.get_phone()

        message = re.findall("您的验证码是(.*?)，", response, re.S)[0]


        self.driver.find_element_by_xpath('.//section[@class="MessageLogin-FsPlX"]/input[@maxlength="8"]').send_keys(message)
        self.driver.find_element_by_class_name('SubmitButton-2wG4T').click()

        time.sleep(3)
        cookies=self.driver.get_cookies()



        # 可以尝试写一个cookie池
        # with open("cookies.txt", "w") as fp:
        #     json.dump(cookies, fp)
        headers={}
        Cookie=""
        for cookie in cookies:

            name=cookie.get('name')
            value=cookie.get('value')
            str_cookie=f"{name}={value};"

            Cookie=Cookie+str_cookie+" "

        print(Cookie)
        print("成功获取账号cookie")
        return Cookie

        # headers['Cookie']=c
        # print(headers)

if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path=r'chromedriver.exe')
    getCookie(driver).get_phone()
# https://github.com/mybdye 🌟


import os, requests, urllib, pydub, base64, ssl, time
from seleniumbase import SB
from datetime import datetime
from urllib.parse import quote
import pyscreenshot as ImageGrab


def recaptcha():
    global body
    print('- recaptcha')
    sb.switch_to_frame('[src*="/recaptcha/api2/anchor?"]')
    print('- switch to frame checkbox')
    checkbox = 'span#recaptcha-anchor'
    print('- click checkbox')
    sb.click(checkbox)
    sb.sleep(4)
    status = checkbox_status()
    tryReCAPTCHA = 1
    while status != 'true':
        sb.switch_to_default_content()  # Exit all iframes
        sb.sleep(1)
        sb.switch_to_frame('[src*="/recaptcha/api2/bframe?"]')
        print('- switch to frame image/audio')
        sb.click("button#recaptcha-audio-button")
        try:
            sb.assert_element('[href*="/recaptcha/api2/payload/audio.mp3?"]')
            print('- normal')
            src = sb.find_elements('[href*="/recaptcha/api2/payload/audio.mp3?"]'
                                   )[0].get_attribute("href")
            print('- audio src:', src)
            # download audio file
            urllib.request.urlretrieve(src, os.getcwd() + audioMP3)
            mp3_to_wav()
            text = speech_to_text()
            #   切回 DEMO
            sb.switch_to_window(1)
            sb.assert_text('Try solving your captchas right now!', 'div[class="section-subtitle"]', timeout=20)
            sb.switch_to_default_content()  # Exit all iframes
            sb.sleep(1)
            sb.switch_to_frame('[src*="/recaptcha/api2/bframe?"]')
            sb.type('#audio-response', text)
            sb.click('button#recaptcha-verify-button')
            sb.sleep(4)
            sb.switch_to_default_content()  # Exit all iframes
            sb.switch_to_frame('[src*="/recaptcha/api2/anchor?"]')
            sb.sleep(1)
            status = checkbox_status()

        except Exception as e:
            print('- 💣 Exception:', e)
            body = str(e)
            sb.switch_to_default_content()  # Exit all iframes
            sb.sleep(1)
            sb.switch_to_frame('[src*="/recaptcha/api2/bframe?"]')
            msgBlock = '[class*="rc-doscaptcha-body-text"]'
            if sb.assert_element(msgBlock):
                body = sb.get_text(msgBlock)
                print('- 💣 maybe block by google\n', body)
                body = '[%s***]\n💣 %s' % (username[:3], body)
                break
            elif tryReCAPTCHA > 3:
                break
            else:
                tryReCAPTCHA += 1
    if status == 'true':
        print('- reCAPTCHA solved!')
        sb.switch_to_default_content()  # Exit all iframes
        return True


def login():
    # window[0]
    print('- login')
    try:
        sb.open(urlBase)
        sb.assert_text('Login', 'td', timeout=20)
        print('- access')
    except Exception as e:
        print('👀 ', e, '\n try again!')
        sb.open(urlBase)
        sb.assert_text('Login your account', 'h2', timeout=20)
        print('- access')
    sb.sleep(1)
    print('- fill [username]')
    sb.type('input[name="email"]', username)
    print('- fill [password]')
    sb.type('input[name="password"]', password)
    print('- click [Login]')
    #sb.click('input[class="btn btn-primary float-end"]')
    sb.click('input[value="Login"]')
    sb.sleep(5)
    i = 1
    try:
        while sb.assert_element('img#captcha', timeout=5):
            if i > 3:
                break
            try:
                msg1 = sb.get_text('td[class="verdana12px-sw"]')
                msg2 = sb.get_text('td[class="verdana14px-rot-b"]')
                print('- [captcha] found!\n%s\n%s', msg1, msg2)
            except Exception:
                msg1 = sb.get_text('td[class="verdana12px-sw"]')
                print('- [captcha] found!\n%s', msg1)

            image = sb.find_element('img#captcha')
            image.screenshot(os.getcwd()+imgCaptcha)
            textCaptcha = captcha()
            #   切回 EU
            sb.switch_to_window(0)
            print('- fill [captcha_code]')
            sb.type('input[name="captcha_code"]', textCaptcha)
            print('- click [Login]')
            sb.click('input[value="Login"]')
            i += 1
            sb.sleep(5)
    except Exception as e:
        print('- [captcha]:', e)
    try:
        while sb.assert_element('input[name="pin"]'):
            if i > 3:
                break
            try:
                pin = get_pin()
            except Exception as e:
                print(e, '\n- Send new PIN')
                sb.click('button[class="btn btn-primary btn-sm"]')
                sb.sleep(5)
                pin = get_pin()
            print('- fill pin')
            sb.type('name=pin', pin)
            sb.click('input[value="Confirm"]')
            i += 1
            sb.sleep(5)

    except Exception as e:
        print('- [Attempted Login]:', e)

    sb.assert_text('Cover Page', 'td[class="td-nav-u-left td-nav-selected"] a')
    print('- login success')
    return True


def captcha():
    # window[1]
    global msgCaptcha
    print('- captcha')
    try:
        sb.open_new_window()
        sb.open(urlCaptcha)
        sb.assert_text('Try solving your captchas right now!', 'div[class="section-subtitle"]', timeout=20)
        print('- access')
    except Exception as e:
        print('👀 ', e, '\n try again!')
        sb.open_new_window()
        sb.open(urlCaptcha)
        sb.assert_text('Try solving your captchas right now!', 'div[class="section-subtitle"]', timeout=20)
        print('- access')

    recaptcha()
    print('- waiting for captcha img upload...')
    sb.choose_file('input[type="file"]', os.getcwd() + imgCaptcha)
    sb.sleep(2)
    print('- click [submit]')
    sb.click('#demo-submit')
    print('- waiting for captcha response...')
    msgCaptcha = sb.get_text('#status-bar-success-message')
    tryCaptcha = 1
    while 'DONE' not in msgCaptcha:
        if tryCaptcha > 20:
            break
        print(msgCaptcha)
        tryCaptcha += 1
        sb.sleep(2)
        msgCaptcha = sb.get_text('#status-bar-success-message')
    print('- final response:', msgCaptcha)
    textCaptcha = sb.find_element('#text_response').get_attribute('value')
    print('- textCaptcha:', textCaptcha)
    if len(textCaptcha) == 3:
        textCaptcha = calculate(textCaptcha)
        print('- final textCaptcha:', textCaptcha)
    sb.driver.close()
    return textCaptcha


def calculate(textCaptcha):
    if textCaptcha[1] == 'X' or textCaptcha[1] == 'x':
        textCaptcha = int(textCaptcha[0]) * int(textCaptcha[2])
    elif textCaptcha[1] == '+':
        textCaptcha = int(textCaptcha[0]) + int(textCaptcha[2])
    elif textCaptcha[1] == '-':
        textCaptcha = int(textCaptcha[0]) - int(textCaptcha[2])
    return textCaptcha


def checkbox_status():
    print('- checkbox_status')
    statuslist = sb.find_elements('#recaptcha-anchor')
    # print('- statuslist:', statuslist)
    status = statuslist[0].get_attribute('aria-checked')
    print('- status:', status)
    return status


def mp3_to_wav():
    print('- mp3_to_wav')
    pydub.AudioSegment.from_mp3(
        os.getcwd() + audioMP3).export(
        os.getcwd() + audioWAV, format="wav")
    print('- mp3_to_wav done')


def speech_to_text():
    print('- speech_to_text')
    sb.open_new_window()
    text = ''
    trySpeech = 1
    while trySpeech <= 3:
        print('- trySpeech *', trySpeech)
        sb.open(urlSpeech)
        sb.assert_text('Speech to text', 'h1')
        sb.choose_file('input[type="file"]', os.getcwd() + audioWAV)
        sb.sleep(5)
        response = sb.get_text('[id*="speechout"]')
        print('- response:', response)
        text = response.split('-' * 80)[1].split('\n')[1].replace('. ', '.')
        print('- text:', text)
        if ' ' in text:
            break
        trySpeech += 1
    sb.driver.close()
    return text


def renew():
    global body
    print('- renew')
    try:
        msgConfirm = sb.get_text('#kc2_content_description')
        if msgConfirm == 'Confirm or change your customer data here.':
            print(msgConfirm)
            sb.click('input[value="Save"]')
            print('- Save clicked')
    except Exception:
        pass
    print('- click [Cover Page]')
    sb.click('a:contains("Cover Page")')
    sb.sleep(4)
    sb.assert_element('#kc2_order_customer_orders_tab_1')
    print('- click [vServer]')
    sb.click('#kc2_order_customer_orders_tab_1')
    try:
        sb.click('input[value="Extend contract"]')
        print('- click button [Extend contract]')
        sb.sleep(4)
        sb.click('input[value="Extend"]')
        print('- click button [Extend]')
        sb.sleep(10)    # Security check, maybe
        try:
            pin = get_pin()
        except Exception as e:
            print(e, '\n- Send new PIN')
            sb.click('button[class="btn btn-primary btn-sm"]')
            sb.sleep(5)
            pin = get_pin()
        sb.sleep(2)
        print('- fill pin')
        sb.type('name=auth', pin)
        #sb.click('button:contains("Continue")')
        sb.click('button[lock="0"]')
        sb.sleep(10)    # Security check, maybe
        confirmation = sb.get_text('#kc2_customer_contract_details_extend_contract_confirmation_dialog_main')
        print('- Contract Extension Confirmation:', confirmation)
        screenshot()
        


    except Exception as e:
        print('- 👀 renew:', e)
        status = sb.get_text('div[class="kc2_order_extend_contract_term_container"]')
        print('- status:', status)
        dateDelta = date_delta_calculate(status.split(' ')[-1])
        if dateDelta > 0:
            body = '[%s***]\n⏰ %s, %d Day(s) Left!' % (username[:3], status, dateDelta)
            print('- msg:', body)


def date_delta_calculate(date_allow):
    date_allow = datetime.strptime(date_allow, '%Y-%m-%d')
    date_now = time.strftime('%Y-%m-%d')
    date_now = datetime.strptime(date_now, '%Y-%m-%d')

    second_allow = time.mktime(date_allow.timetuple())
    second_now = time.mktime(date_now.timetuple())

    second_delta = int(second_allow) - int(second_now)
    date_delta = int(second_delta / 60 / 60 / 24)
    return date_delta


def get_pin():
    print('- get pin')
    response = requests.get(url=MAILPARSER)
    pin = response.json()[0]['pin']
    print('- pin:', pin)
    return pin


def screenshot():
    global body
    print('- screenshot')
    # grab fullscreen
    im = ImageGrab.grab()
    # save image file
    im.save("fullscreen.png")
    
    #sb.save_screenshot(imgFile, folder=os.getcwd())
    print('- screenshot done')
    sb.open_new_window()
    print('- screenshot upload')
    sb.open('http://imgur.com/upload')
    # sb.choose_file('input[type="file"]', os.getcwd() + '/' + imgFile)
    sb.choose_file('input[type="file"]', "fullscreen.png")
    sb.sleep(6)
    imgUrl = sb.get_current_url()
    i = 1
    while not '/a/' in imgUrl:
        if i > 3:
            break
        print('- waiting for url... *', i)
        sb.sleep(2)
        imgUrl = sb.get_current_url()
        i += 1
    print('- 📷 img url:', imgUrl)
    body = imgUrl
    print('- screenshot upload done')
    sb.driver.close()
    return imgUrl


def url_decode(s):
    return str(base64.b64decode(s + '=' * (4 - len(s) % 4))).split('\'')[1]


def push(body):
    print('- body: %s \n- waiting for push result' % body)
    # bark push
    if barkToken == '':
        print('*** No BARK_KEY ***')
    else:
        barkurl = 'https://api.day.app/' + barkToken
        barktitle = quote(urlBase, safe='')
        barkbody = quote(body, safe='')
        rq_bark = requests.get(url=f'{barkurl}/{barktitle}/{barkbody}?isArchive=1')
        if rq_bark.status_code == 200:
            print('- bark push Done!')
        else:
            print('*** bark push fail! ***', rq_bark.content.decode('utf-8'))
    # tg push
    if tgBotToken == '' or tgUserID == '':
        print('*** No TG_BOT_TOKEN or TG_USER_ID ***')
    else:
        tgbody = urlBase + '\n\n' + body
        server = 'https://api.telegram.org'
        tgurl = server + '/bot' + tgBotToken + '/sendMessage'
        rq_tg = requests.post(tgurl, data={'chat_id': tgUserID, 'text': tgbody}, headers={
            'Content-Type': 'application/x-www-form-urlencoded'})
        if rq_tg.status_code == 200:
            print('- tg push Done!')
        else:
            print('*** tg push fail! ***', rq_tg.content.decode('utf-8'))
    print('- finish!')


##
try:
    username = os.environ['USERNAME']
except:
    # 本地调试用，在线勿填
    username = ''

try:
    password = os.environ['PASSWORD']
except:
    # 本地调试用，在线勿填
    password = ''

try:
    MAILPARSER = os.environ['MAILPARSER']
except:
    # 本地调试用，在线勿填
    MAILPARSER = ''

try:
    barkToken = os.environ['BARK_TOKEN']
except:
    # 本地调试用
    barkToken = ''
try:
    tgBotToken = os.environ['TG_BOT_TOKEN']
except:
    # 本地调试用
    tgBotToken = ''
try:
    tgUserID = os.environ['TG_USER_ID']
except:
    # 本地调试用
    tgUserID = ''

##
urlBase = url_decode('c3VwcG9ydC5ldXNlcnYuY29t')
urlCaptcha = url_decode('aHR0cHM6Ly90cnVlY2FwdGNoYS5vcmcvZGVtby5odG1s')
urlSpeech = url_decode(
    'aHR0cHM6Ly9henVyZS5taWNyb3NvZnQuY29tL2VuLXVzL3Byb2R1Y3RzL2NvZ25pdGl2ZS1zZXJ2aWNlcy9zcGVlY2gtdG8tdGV4dC8jZmVhdHVyZXM==')
##
body = ''
msgCaptcha = ''
audioMP3 = '/' + urlBase + '.mp3'
audioWAV = '/' + urlBase + '.wav'
#imgFile = urlBase + '.png'
imgCaptcha = '/captcha.png'
# 关闭证书验证
ssl._create_default_https_context = ssl._create_unverified_context

with SB(uc=True) as sb:  # By default, browser="chrome" if not set.
    print('- 🚀 loading...')
    if urlBase != '' and username != '' and password != '':
        try:
            if login():
                renew()
        except Exception as e:
            print('💥', e)
            try:
                screenshot()
            finally:
                push(str(e))
        push(body)
    else:
        print('- please check urlBase/username/password')

# END

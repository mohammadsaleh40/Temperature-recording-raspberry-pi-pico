import uos
files = uos.listdir()
print(files)
from machine import Pin, I2C,PWM , ADC , UART
from ssd1306 import SSD1306_I2C
import onewire, ds18x20
from onewire import OneWireError
import utime 
from machine import RTC
import json

def baksh(n=1):
    # تعریف لامپ روی بورد
    led_onboard = Pin(25, Pin.OUT)
    for i in range(n):
        for j in range(10,20):
            t=1/j
            led_onboard.value(1)
            utime.sleep(t)
            led_onboard.value(0)
            utime.sleep(t)


#دکمه خاموش کردن کار
button = Pin(16, Pin.IN, Pin.PULL_DOWN)

# چک کردن ورودی برق USB 
USBpower = Pin(24, Pin.IN) 


#زمان پیش‌فرض
rtc = RTC()





a = utime.localtime()
print("zaman is : ",a)





start_time = utime.localtime()
ferq = 0
neyaz_be_tanzim_zaman = True
dastoor_ghabl = 0


#روشن کردن مثبت نمایشگر
led_p =  Pin(4, Pin.OUT)
led_p.value(1)
print("روشن شد")


#تعریف نمایشگر
baksh()
print("khob ...")
i = I2C(1, scl=Pin(3), sda=Pin(2), freq=10000)
print("bad az i2c ")


oled = SSD1306_I2C(128, 64, i)
print("moshkeli nabood")

text_test = "saaaalam"


oled.text(text_test, 19 , 30)
oled.show()
utime.sleep(0.3)
oled.fill(0)
oled.show()


#تعریف بلوتوث
id = 0
rx = Pin(1)
tx = Pin(0)
baudrate = 9600 # default is 9600
print("id : ", id , " tx : ", tx , " rx : ", rx)

# create the UART

uart = UART(id, 9600 ,tx=tx, rx=rx)

#روشن کردن مثبت ذما سنج
ds_p =  Pin(18, Pin.OUT)
ds_p.value(1)


ds_pin = Pin(17)

ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()
#صبر برای وصل شدن بلوتوث
#yes_or_no = input("rad?")
baksh()
print('Found DS devices: ', roms)

uart.write('Found DS devices: '+ str(roms)+" \r\n")
uart.write(" salam be barname ma khosh amadid\r\n")
uart.write("فارسی چطوره؟ \r\n")




#تعداد باری که باید دما اعلام بشه
n= 0
ersal_dama = True
time = utime.time()
record = 0    

if "dafeha.txt" in files:
    with open ("dafeha.txt" , "r") as f:
        dafe = int(f.read())
    with open ("dafeha.txt" , "w") as f:
        f.write(str(dafe+1))
else:
    with open ("dafeha.txt" , "w") as f:
        f.write(str(0))
        dafe = 0

while True:
    
    a = rtc.datetime()
    m=""
    s=""
    for x in range(0,3):
        m+=str(a[x])+":"
    m = m[:-1]
    for x in range(4,7):
        s+=str(a[x])+":"
    s = s[:-1]
    u=""
    if USBpower() == 0:
        u="USB OFF"
    elif USBpower() == 1:
        u="USB ON"
    else:
        u="USB ERROR"

    
    try:
        ds_sensor.convert_temp()
    except OneWireError:
        pass
    try:
        dama = ds_sensor.read_temp(roms[0])
        oled.text(str(dama), 0, 56)
        #این اگر فعال بشه دائم دما برای گیرنده ارسال می‌شه
        #uart.write(str(ds_sensor.read_temp(roms[0]))+"\r\n")
    except:
        dama = "DS ERROR"
        oled.text(dama,1,56)
    
    if uart.any() > 0:
        data = str(uart.read())[2:-5]
        if "temp" in data:
            if data.split()[0] =="temp":
                try:
                    n = int(str(data.split()[1:])[2:-2])
                except:
                    uart.write("yek moshkeli hast \""+str(data.split()[1:])+"\" adad nist."+"\r\n")
                

        else:
            uart.write("motavajeh nashodam\r\n")
    
    
    if n>0 and time<utime.time():
        time = utime.time()
        n-=1
        uart.write(str(ds_sensor.read_temp(roms[0]))+"\r\n")
    statvfs = str(uos.statvfs("/"))
    stat = str(uos.stat("/"))

    
        
    js = json.dumps({'saat': s, 'sal': m , "usb": u , "dama":dama, "stat":stat , "statvfs":statvfs} )
    js_ezafe = {str(record):js}
    if record == 0:
        with open("recods_"+str(dafe)+".json", "w") as file:
            file.seek(0)
            json.dump(js_ezafe, file )
    else:
        with open("recods_"+str(dafe)+".json", "r+") as file:
            file_data = json.loads(file.read())
            file_data.update(js_ezafe)
            file.seek(0)
            json.dump(file_data, file )
    
    oled.text(s,0,8)
    oled.text(m,4,0)    
    oled.text(u,4,24)
    oled.text(stat,4,32)
    oled.text(statvfs,4,40)
    
    oled.show()
    oled.fill(0)
    record += 1
    if button.value():
        print(uos.getcwd())
        break


oled.fill(0)
oled.show()

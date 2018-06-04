
from passlib.hash import sha512_crypt

password=sha512_crypt.encrypt("password")
#print(sha512_crypt.encrypt("password"))
#print(sha512_crypt.verify("password", password))

password_file=open("password","wb")
password_file.write(password.encode())
password_file.close()
pf=open("password","rb")
print(sha512_crypt.verify("paassword",pf.read()))

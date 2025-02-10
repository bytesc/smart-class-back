from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# 生成RSA密钥对
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# 将私钥序列化为PEM格式
pem_private_key = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# 从私钥中获取公钥
public_key = private_key.public_key()

# 将公钥序列化为PEM格式
pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# 保存私钥和公钥到文件
private_key_path = 'private_key.pem'
public_key_path = 'public_key.pem'

with open(private_key_path, 'wb') as f:
    f.write(pem_private_key)

with open(public_key_path, 'wb') as f:
    f.write(pem_public_key)



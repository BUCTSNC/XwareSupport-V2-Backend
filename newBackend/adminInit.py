import bcrypt,json

config = json.load(open("./adminConfig.json","r"))
import manageAPI.models

def init():
    username = config['Username']
    password = config['Password']
    salt = bcrypt.gensalt()
    saltStr = salt.hex()
    password_with_salt = bcrypt.hashpw(str(password).encode("utf8"),salt).hex()
    owners = manageAPI.models.User.objects.filter(auth=5)
    if owners.count() != 0:
        owners.delete()
    manageAPI.models.User(
        username=username,
        passwordHashWithSalt=password_with_salt,
        salt=saltStr,
        auth=5,
        nickname="admin",
    ).save()







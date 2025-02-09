####Get your discord token:

first Login your discord account
Go to developer mode (F12)
GO to console   type    (allow pasting )

copy and paste 

```
(
    webpackChunkdiscord_app.push(
        [
            [''],
            {},
            e => {
                m=[];
                for(let c in e.c)
                    m.push(e.c[c])
            }
        ]
    ),
    m
).find(
    m => m?.exports?.default?.getToken !== void 0
).exports.default.getToken()
```

get discord token and save 



####HOW TO GET GEMINI API :

go to : https://aistudio.google.com/apikey

    Login with your google accounts
    Create API Key
    Copy API Key

    
####guide for discord auto

```git clone    ```

 
```screen -S discord```

```cd discord-gmni```

```sudo apt update && sudo apt upgrade -y```

```
apt install python3-pip
apt install python3-venv
pyton3 -m venv discord
source discord/bin/activate
pip install -r requirements.txt 
```

###replace discord token and gemeni api 
```nano .env```

ctrl X+Y  ENTER 

###start bot 

```
pyton3 discord.py 
```

####set channel id 

Go to the channel where you want the bot to be active.

like this 
![discord](https://github.com/user-attachments/assets/d2dbdedc-405b-4947-8fff-1f76ba0d4f28)






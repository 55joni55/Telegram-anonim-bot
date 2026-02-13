
<div align="center">
  <img src="https://static.wikia.nocookie.net/slimerancher/images/0/0f/Glitch_Slime_SecretStyle_SP.png/revision/latest?cb=20241012200654" alt="GLITCH.EXE" width="300"/>
</div>

# 🤖 Two Bots - Two Philosophies of Anonymity

## 📁 Anonim.py - Absolute Privacy
A script for those who prioritize user confidentiality above all.

🔐 The Core: COMPLETE ANONYMITY
The administrator sees no sender data whatsoever:
 - First Name, Last Name, Username, Avatar, User ID

👁️ Visible to the Admin:
 - Content Type (text/photo/video), Message Content, Timestamp

⚠️ Note:
 - Telegram Premium stickers and emojis are not supported; they will appear as regular static stickers (losing animation and quality).


## 📁 Anonim_forward.py — The Illusion of Anonymity (Full Control)
 - A script for administrators who need to see everything while keeping users in the dark.

🎭 How It Works:
 - Users believe they are anonymous, but you see the maximum amount of data.

👁️ What YOU (the admin) see:
 - First and Last Name, Username (@handle), Exact Timestamp, Full content and type, Forward restriction status (whether content is protected)

🚀 Advantages
 Full Telegram Premium support:
 - Animated stickers in original quality, Premium emojis, Unique stickers and animations, All exclusive content from premium users


⚙️ INSTALLATION & SETUP (for both scripts)

Install the dependency. The scripts are written for aiogram 2.x, so run the following command in your terminal:

bash
- pip install aiogram

Before the first launch, be sure to open the script file and modify the following parameters:
- TOKEN - insert your bot's token, obtained from @BotFather.
- ACCOUNT_ID - enter your numeric user ID (you can get it from [@G5_55_5G_bot](https://t.me/G5_55_5Gs_bot)). This is the account that will receive all messages forwarded from users.
- start_command_gid and start_command_text - you can customize the welcome text and the GIF animation that the bot sends in response to the /start command.

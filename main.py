import telebot
import time
import json 
import sqlite3

bot = telebot.TeleBot("") #Ключ для бота 


trade_ban_list = ["продам"] # Спам-лист для продажи
polit_ban_list = ["украина","путин","власть","зеленский"] # Политический Спам-лист
message_ok = False
chat_id = -1001601095799 # ID Чата, берется из консоли 

def long_delete_message(message_id):
	time.sleep(5)
	delete_message(message_id+1)

def warn_user(message):
	message_reply = message.reply_to_message
	if message_reply != None:
		tg_id = message.reply_to_message.from_user.id
		first_name = message.reply_to_message.from_user.first_name
		
		conn = sqlite3.connect('warn_list.db')
		cur = conn.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS users(userid INT PRIMARY KEY,warns INT)")
		conn.commit()
		finded = False
		cur.execute("SELECT * FROM users;")
		all_results = cur.fetchall()
		for i in all_results:
			if tg_id in i:
				warns = i[1]
				warns += 1
				cur.execute('UPDATE users SET warns=? WHERE userid=?',(warns,tg_id))
				conn.commit()
				if warns == 3:
					send_message("Внимание! У вас уже 3 предупреждения. Ещё одно приведёт к блокировке в чате!")
				elif warns > 3:
					send_message("Предупреждения 4. Блокирую пользователя..")
					delete_message(message.reply_to_message.id)
					bot.ban_chat_member(chat_id,message.reply_to_message.from_user.id)
					cur.execute("DELETE FROM users WHERE userid = ?",(message.from_user.id,))
					conn.commit()
				else:
					send_message(f"Пользователю выдано {warns} предупреждение.")
				delete_message(message.reply_to_message.id)
				finded = True
		conn.commit()

		if not finded:
			warns = 1
			cur.execute("INSERT INTO users VALUES(?,?)",(tg_id,warns))
			conn.commit()
			delete_message(message.reply_to_message.id)
			send_message(f"Пользователю выдано {warns} предупреждение.")
	else:
		tg_id = message.from_user.id
		first_name = message.from_user.first_name
		
		conn = sqlite3.connect('warn_list.db')
		cur = conn.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS users(userid INT PRIMARY KEY,warns INT)")
		conn.commit()

		finded = False
		cur.execute("SELECT * FROM users;")
		all_results = cur.fetchall()
		for i in all_results:
			if tg_id in i:
				warns = i[1]
				warns += 1
				cur.execute('UPDATE users SET warns=? WHERE userid=?',(warns,tg_id))
				conn.commit()
				if warns == 3:
					if not message.from_user.username:
						send_message(f"Внимание! {message.from_user.first_name} У вас уже 3 предупреждения. Ещё одно приведёт к блокировке в чате!")
					else:
						send_message(f"Внимание! @{message.from_user.username} У вас уже 3 предупреждения. Ещё одно приведёт к блокировке в чате!")
				elif warns > 3:
					if not message.from_user.username:
						send_message(f"Предупреждения 4. Блокирую пользователя {message.from_user.first_name}")
					else:
						send_message(f"Предупреждения 4. Блокирую пользователя @{message.from_user.username}")
					bot.ban_chat_member(chat_id,message.from_user.id)
					cur.execute("DELETE FROM users WHERE userid = ?",(message.from_user.id,))
					conn.commit()
				else:
					if not message.from_user.username:
						send_message(f"Пользователю {message.from_user.first_name} выдано {warns} предупреждение.")
					else:
						send_message(f"Пользователю @{message.from_user.username} выдано {warns} предупреждение.")
				finded = True
		conn.commit()

		if not finded:
			warns = 1
			cur.execute("INSERT INTO users VALUES(?,?)",(tg_id,warns))
			conn.commit()
			if not message.from_user.username:
				send_message(f"Пользователю {message.from_user.first_name} выдано {warns} предупреждение.")
			else:
				send_message(f"Пользователю @{message.from_user.username} выдано {warns} предупреждение.")

def send_message(text):
	bot.send_message(chat_id,text)

def delete_message(ids):
	bot.delete_message(chat_id,ids)

@bot.message_handler(commands=['clear'])
def clear_warns(message):
	conn = sqlite3.connect('warn_list.db')
	cur = conn.cursor()
	cur.execute("DELETE FROM users WHERE userid = ?",(message.reply_to_message.from_user.id,))
	conn.commit()
	if not message.reply_to_message.from_user.username:
		send_message(f"Очищены все предупреждение пользователя {message.reply_to_message.from_user.first_name}.")
	else:
		send_message(f"Очищены все предупреждение пользователя  @{message.reply_to_message.from_user.username} .")

@bot.message_handler(commands=['warn'])
def warnUser(message):
	user = message.from_user.id
	user_status = bot.get_chat_member(chat_id,user).status
	if user_status != "member":
		if not message.reply_to_message:
			bot.reply_to(message,"Отправь эту команду ответом на сообщение нарушителя.")
		else:
			warn_user(message)
	else:
		bot.reply_to(message,"Эту команду могут использовать только админы чата.")

def bad_word_warn(message,text):
	time.sleep(1)
	delete_message(message.id)
	if not message.from_user.username:
		send_message(f"Слушай, {message.from_user.first_name}{text}")
	else:
		send_message(f"Слушай, @{message.from_user.username}{text}")
	long_delete_message(message.id)
	warn_user(message)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
	print(message)
	user = message.from_user.id
	user_status = bot.get_chat_member(chat_id,user).status
	if user_status == "member":
		for i in polit_ban_list:
			if i in message.text.lower():
				bad_word_warn(message," лучше не поднимать такие темы..")
		for i in trade_ban_list:
			if i in message.text.lower():
				bad_word_warn(message," это не Авито, а Костромской чат!")

bot.infinity_polling()

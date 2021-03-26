import telebot
import time

bot = telebot.TeleBot("YOUR_KEY")

user_ids = set()
global_vars = {id : [0, 0, 0, '', set(), {}] }

time_1 = 0
time_2 = 0
start_time = 0

previous_act = ''

activities = set()

action_times = {activity: 0 for activity in activities}

def stamp_to_sec(timemark):
    sec = int(timemark[17:19])
    min = int(timemark[14:16]) * 60
    hrs = int(timemark[11:13]) * 60 * 60
    return sec + min + hrs

@bot.message_handler(commands=['start'])
def welcome(message):

    if message.from_user.id not in user_ids:
        user_ids.add(message.from_user.id)
    bot.send_message(message.from_user.id,
                     "Привет, я буду вести статистику твоего дня \n"
                     "Пиши сюда свои активности, а я посчитаю сколько времени ты на них тратишь\n"
                     "Пиши каждый раз когда начинаешь что-то новое\n\n например - читаю\n напиши"
                     " /stats чтобы получить статистику")

@bot.message_handler(commands=['stats'])
def stats(message):
    global start_time, activities, action_times, time_2, time_1
    #all_period = stamp_to_sec(time.ctime(time_2 - start_time))

    time_2 = message.date
    action_times[previous_act] += stamp_to_sec(time.ctime(time_2 - time_1))

    stat_string = "всего ты-\n\n"
    for activity in activities:
        stat_string += "{0} - {1} ч {2} мин {3} сек \n".format(activity, action_times[activity] // 3600,
                                                                     action_times[activity] // 60 - action_times[activity] // 3600 * 60,
                                                                     action_times[activity] % 60)
    bot.send_message(message.from_user.id, stat_string)


@bot.message_handler(commands=['reset'])
def reset(message):
    global start_time, time_1, time_2, previous_act, action_times, activities
    start_time = message.date
    bot.send_message(message.from_user.id, "Статистика обнулена!")

    time_1 = 0
    time_2 = 0
    start_time = 0

    previous_act = ''  # previous activity

    activities = set()
    action_times = {activity: 0 for activity in activities}


@bot.message_handler(content_types=['text'])
def getting_message_time(message):
    global time_1, time_2, start_time, activities, action_times, previous_act, start_time

    # is activity new?
    if message.text not in activities:
        action_times.update({message.text: 0})

    activities.add(message.text)

    # getting time_1 and then assign it to ACTIVITY in dict
    if time_1 == 0:
        time_1 = message.date
        start_time = time_1
        previous_act = message.text
    else:
        time_2 = message.date

        #
        #bot.send_message(message.from_user.id, stamp_to_sec(time.ctime(time_2 - time_1)))
        action_times[previous_act] += stamp_to_sec(time.ctime(time_2 - time_1)) - 10800

        time_1 = time_2
        previous_act = message.text

    print(action_times)



bot.polling()

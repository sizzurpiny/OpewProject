import asyncio
import os
import threading
import time
import pathlib
import yt_dlp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from pydub import AudioSegment
from pytube import YouTube
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

Apitoken = "" # Апи токен для бота
bot = Bot(token=Apitoken)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

messageMain = ''

caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"

driver = webdriver.Chrome(desired_capabilities=caps)
driver.get('https://www.youtube.com/results?search_query=')


class Dowload(StatesGroup):
    dowload = State()


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


async def get_video_results(message, Id_user):
    print("начал")

    driver.get('https://www.youtube.com/results?search_query=' + message)
    time.sleep(0.25)
    youtube_data = []
    link = driver.find_element(By.CSS_SELECTOR, '.text-wrapper.style-scope.ytd-video-renderer').find_element(
        By.CSS_SELECTOR,
        '.title-and-badge.style-scope.ytd-video-renderer a').get_attribute('href')

    youtube_data.append(link)
    youtube_data.append(YouTube(youtube_data[0]).title)
    length = YouTube(youtube_data[0]).length
    youtube_data.append(True)
    youtube_data.append(YouTube(youtube_data[0]).video_id)

    if (length < 900):
        print("Закинул")
        ROOT_DIR = os.path.abspath(f'audio\\{youtube_data[1]}☢☣☯☮☣☬☪{Id_user}')
        # return youtube_data

        # ☢☣☯☮☣☬☪

        with yt_dlp.YoutubeDL({
            'format': 'bestaudio/best',
            'outtmpl': 'audio\\' + youtube_data[1] + '.wav',
            'progress_hooks': [my_hook]
        }) as ydl:
            ydl.download([youtube_data[0]])
        if not os.path.exists(f'{ROOT_DIR}.mp3'):
            AudioSegment.from_file(f'audio\\{youtube_data[1]}.wav').export(f"{ROOT_DIR}.mp3", format="mp3")
            os.remove(f'audio\\{youtube_data[1]}.wav')

    else:
        print(youtube_data[1] + " too large")
        youtube_data[2] = False
        return youtube_data



#############################   https://stackoverflow.com/questions/59645272/how-do-i-pass-an-async-function-to-a-thread-target-in-python


@dp.message_handler(state=Dowload.dowload)
async def dowload(message: types.Message, state: FSMContext):
    await message.reply("Ожидай, сейчас найду...")

    tear = threading.Thread(target=asyncio.run, args=(get_video_results(message.text, message.chat.id),))
    tear.start()
    await state.finish()

    # os.remove(f'audio\\{title[3]}.wav')
    # audio = open(f'audio/{title[3]}.mp3', 'rb')
    # await bot.send_audio(message.chat.id, audio, title="@OpewBot. " + str(title[1]),
    #                     caption=f"Трек: {title[1]}"
    #                             "\nМного информации о новой музыке и об обновлениях в нашей группе @none123123123"
    #                             "\nПодписывайся!")

    # os.remove(f'audio\\{title[3]}.mp3')###############################################################


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    tt = time.time()
    print(time.time() - tt)

    fileDir = os.path.abspath(f'audio')
    fileExt = r"*.mp3"

    listOfTracks = list(pathlib.Path(fileDir).glob(fileExt))
    if len(listOfTracks) != 0:
        for part in listOfTracks:
            biba = str(part)
            boba = biba.replace(fileDir, '')
            splittedList = boba.split('☢☣☯☮☣☬☪')
            print(biba + "\n" + boba + "\n" + splittedList[0] + "\n" + splittedList[1])

    await message.answer(
        text=f"Привет, {message.from_user.full_name}"
             f"\nПиши /find и находи любой трек! \nЛибо /finds, чтобы найти сразу несколько "
             f"\nКоманда /help поможет тебе разобраться")



@dp.message_handler(commands=['find'])
async def send_welcome(message: types.Message):
    print(message.from_user.full_name + " начал загрузку")
    await message.answer(
        text=f"Скидывай исполнителя и песню, сейчас загружу\n")
    await Dowload.dowload.set()


@dp.message_handler(content_types=['text'])
async def reply_text(message: types.Message):
    await message.reply("Не понимаю. \nЕсли хочешь найти трек, то напиши команду /find.\nИли /help для справки")


async def periodic(sleep_for):  # Проверка на: существует ли файл мп3
    fileDir = os.path.abspath(f'audio')
    fileExt = r"*.mp3"

    while True:
        await asyncio.sleep(sleep_for)
        listOfTracks = list(pathlib.Path(fileDir).glob(fileExt))
        #print(threading.active_count())
        if len(listOfTracks) != 0:
            for part in listOfTracks:
                try:
                    buff1 = str(part)
                    buff2 = buff1.replace(fileDir, '')
                    buff2 = buff2.replace('.mp3', '')
                    splittedList = buff2.split('☢☣☯☮☣☬☪')
                    os.rename(buff1, fileDir + splittedList[0] + '.mp3')
                    audio = open(f'audio{splittedList[0]}.mp3', 'rb')
                    await bot.send_audio(splittedList[1], audio,
                                         title="@OpewBot. " + str(splittedList[0][1:]),
                                         caption=f"Трек: {splittedList[0][1:]}"
                                                 "\nМного информации о новой музыке и об обновлениях в нашей группе @none123123123"
                                                 "\nПодписывайся!"
                                         )
                    os.remove(f'audio{splittedList[0]}.mp3')

                except Exception:
                    pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(periodic(0.5))
    executor.start_polling(dp, skip_updates=True)



# async def dowloaded(title, ID, ROOT_DIR):
#    with yt_dlp.YoutubeDL({
#       'format': 'bestaudio/best',
#      'outtmpl': 'audio\\' + ID + '.wav',
#     'progress_hooks': [my_hook]
# }) as ydl:
#   ydl.download([title])


# async def conv(ROOT_DIR, message, title):
#   if not os.path.exists(f'{ROOT_DIR}.mp3'):
#      AudioSegment.from_file(f"{ROOT_DIR}.wav").export(f"{ROOT_DIR}.mp3", format="mp3")
# audio = open(f'audio/{title[3]}.mp3', 'rb')
# await bot.send_audio(message.chat.id, audio, title="@OpewBot. " + str(title[1]),
#                    caption=f"Трек: {title[1]}"
#                           "\nМного информации о новой музыке и об обновлениях в нашей группе @none123123123"
#                          "\nПодписывайся!")

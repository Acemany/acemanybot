#!/usr/bin/env python

from collections.abc import Callable, Generator  # pylint: disable=E0401
from json import dump, load, JSONDecodeError
from asyncio import run as aiorun
from typing import Any

from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram import Bot, Dispatcher
from aiogram.types import Message

from aiofile import async_open as aiopen
from requests import get as r_get
from dotenv import dotenv_values


async def log(m: str):
    "Save something that will possibly helpful when error or something happens"

    async with aiopen('./log.txt', 'a') as af:
        await af.write(f'{m}\n')


def unorid(m: Message) -> str:
    "Returns @name of the user, othervise returns his id"

    if m.from_user.username is None:
        return f"@{m.from_user.username}"
    return f"{m.from_user.id}"


def usrorgroup(_id: int) -> str:
    "Returns link to user or group by id"

    if _id >= 0:
        return f"tg://user?id={_id}"
    return f"t.me/c/{str(_id)[4:]}"


async def reg(m: Message):
    "Saves call for statistics and smth"

    command: str = m.text.split()[0].split("@")[0]
    await log(f'[I] {unorid(m)}: "{command}"')

    if m.chat.id not in count:
        count[m.chat.id] = {}
    if m.from_user.id not in count[m.chat.id]:
        count[m.chat.id][m.from_user.id] = {}

    count[m.chat.id][m.from_user.id][command] = count[m.chat.id][m.from_user.id].get(
        command,
        0
    ) + 1


def raises(handler: Callable[..., Any]) -> Callable[..., Any]:
    "Just a handler"

    async def wrapped(message: Message) -> Any:
        try:
            return await handler(message)
        except Exception as e:
            await log(f'[E] {unorid(message)}: "{message.text.replace('\n', '\\n')}"\n{e}\n')
            if message.text not in ("/catgif", "/catgif@acemanybot"):
                await message.reply("Сталася критична помилка: \nВiдвал сраки")
            elif e is TelegramBadRequest:
                await message.reply("Похоже котик затерялся.. Попробуй ещё разок!")
            raise e

    return wrapped


async def get(url: str) -> dict[str, object]:
    "Wrapper around `requests.get`"

    try:
        if url[4] == "s":
            url = url[:4] + url[5:]
        return r_get(url,
                     proxies={'http': 'socks5://0.0.0.0:1080',
                              'https': 'socks5://0.0.0.0:1080'},
                     #          verify=False,
                     timeout=10,
                     ).json()
    except JSONDecodeError as e:
        print(url)
        resp = r_get(url, timeout=10)
        print(f"[{resp.status_code}] '{resp.text}'")
        raise e


def parse_args(s: str) -> list[str]:
    "Returns args for command, like `\"/safe arg0 arg1 arg2\"` -> [arg0, arg1, arg2]"

    return s


def separate_every(s: str, n: float) -> Generator[str, None, None]:
    "Separates string `s` every `n` charscters"

    if n == 0:
        raise ValueError('Separate by every 0 symbols?')
    return (s[n*i:n*(i+1)]
            for i in range(int(1+(len(s)-1)/n)))


with open('count.json', 'r', encoding='utf-8') as f:
    counts = load(f)

    count: dict[int, dict[int, dict[str, int]]] = {
        int(chat): {
            int(user): j.items() for user, j in i.items()
        } for chat, i in counts.items()
    }


secrets: dict[str, str] = dotenv_values('.env')  # type: ignore

TOKEN: str = secrets["BOT_TOKEN"]
bot: Bot = Bot(token=TOKEN)
dp: Dispatcher = Dispatcher()
miha: set[int] = {1987557308, 6076298659, *secrets["ALLOWED"].split(',')}
tagsdict = {
    "illustration": 1, "girl": 2, "black_hair": 3, "sportswear": 4, "sword": 5,
    "kemonomimi": 6, "flowers": 7, "catgirl": 8, "white_hair": 9, "loli": 10,
    "plants": 11, "blue_hair": 12, "pink_hair": 13, "purple_hair": 14, "exposed_girl_breasts": 15,
    "exposed_anus": 16, "pussy": 17, "dick": 18, "maid": 19, "beach": 20, "reading": 21,
    "mountain": 22, "night": 23, "gloves": 24, "original_style": 25, "brown_hair": 26,
    "sunny": 27, "rain": 28, "shorts": 29, "weapon": 30, "bikini": 31, "ice_cream": 32,
    "tree": 33, "bunny_girl": 34, "dress": 35, "usagimimi": 36, "school_uniform": 37,
    "guitar": 38, "baggy_clothes": 39, "wet": 40, "yuri": 41, "red_hair": 42, "glasses": 43,
    "anal": 44, "futanari": 45, "masturbating": 46, "threesome": 47, "kissing": 48,
    "skirt": 49, "blonde_hair": 50, "horsegirl": 51, "boy": 52, "large_breasts": 53,
    "medium_breasts": 54, "small_breasts": 55, "flat_chest": 56, "furry": 57,
}


@dp.message(Command('start'))
async def start(message: Message):
    """
    "Hello, world!" message
    """

    await message.reply('Привет! Я жалкая копия бота Червяка')


@dp.message(Command('help'))
async def help_list(message: Message):
    "List of commands"

    await message.reply('/cat - фото котэта\n'
                        '/catgif - гифка с котэм\n'
                        '/dog - пёсель\n'
                        '/fox - лись\n'
                        '/neko - кошкодевочка\n'
                        '/girl - оняме девочка\n'
                        '/safe - SFW картиночки, с промптом\n'
                        '/help - Этот список')


@dp.message(Command('stats'))
@raises
async def stats(m: Message):
    "Stats that only i can see, used for... IDK tbh, it just looks fancy"

    if m.chat.id not in miha:
        print('Nonadmin tried to get stats:', m.from_user.id)
        return

    tmp = ""
    for chat, i in sorted(count.items()):
        tmp += f"[{chat}]({usrorgroup(chat)}):\n"
        for user, j in sorted(i.items()):
            if chat != user:
                tmp += f"`  `[{user}]({usrorgroup(user)}):\n"
            for msg, c in sorted(j.items()):
                tmp += f"`  {'  ' if chat != user else ''}`{msg}: {c}\n"

    await m.reply(tmp, parse_mode='markdown')


@dp.message(Command('cat'))
@raises
async def cat(m: Message):
    "Cat picture"

    await reg(m)

    url = (await get('https://api.thecatapi.com/v1/images/search'))[0]["url"]

    try:
        await m.reply_photo(url)
    except Exception as e:
        print(url)
        raise e


@dp.message(Command('catgif'))
@raises
async def catgif(m: Message):
    "Cat gif"

    await reg(m)

    url: str = f"https://cataas.com/cat/{(await get('http://cataas.com/cat/gif?json=true'))['_id']}.gif"

    try:
        await m.reply_animation(url)
    except Exception as e:
        print(url)
        raise e


@dp.message(Command('dog'))
@raises
async def dog(m: Message):
    "Dog picture"

    await reg(m)

    url = (await get('https://api.thedogapi.com/v1/images/search'))[0]["url"]

    try:
        await m.reply_photo(url)
    except Exception as e:
        print(url)
        raise e


@dp.message(Command('fox'))
@raises
async def fox(m: Message):
    "Fox picture"

    await reg(m)

    url = (await get('https://randomfox.ca/floof'))["image"]

    try:
        await m.reply_photo(url)
    except Exception as e:
        print(url)
        raise e


@dp.message(Command('neko'))
@raises
async def neko(m: Message):
    "Neko picture"

    await reg(m)

    args = parse_args(m.text)
    lim: int = args[0] if len(args) > 0 and args[0].isdigit() else 1
    urls = (await get(f'https://nekos.best/api/v2/neko?amount={lim}'))["results"]

    try:
        media_group = MediaGroupBuilder()
        for i in urls:
            media_group.add_photo(i["url"])
        await m.answer_media_group(media_group.build())
    except Exception as e:
        print(urls)
        raise e


@dp.message(Command('safe'))
@raises
async def safe(m: Message):
    """
    Picture from safebooru
    `/safe count tag1 tag2 page`
    """

    await reg(m)

    args = parse_args(m.text)
    limit: int = args[0] if len(args) > 0 and args[0].isdigit() else 1
    pid: int = args[-1] if len(args) > 1 and args[0].isdigit() and args[-1].isdigit() else 0
    tags: str = ('&tags='+'%20'.join(
        parse_args(m.text)[int(args[0].isdigit()):
                           len(parse_args(m.text))-int(len(args) > 1 and args[-1].isdigit())
                           ])) if " " in m.text else ""
    prev = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&limit={limit}&json=1{tags}&pid={pid}"

    urls = await get(prev)
    if urls is None:
        await m.reply('Не нашла ничего подходящего(')
        return

    try:
        try:
            media_group = MediaGroupBuilder()
            for i in urls:
                media_group.add_photo(i["file_url"])
            await m.answer_media_group(media_group.build())
        except TelegramBadRequest:
            media_group = MediaGroupBuilder()
            for i in urls:
                media_group.add_photo(i["sample_url"])
            await m.answer_media_group(media_group.build())
    except Exception as e:
        print(urls)
        raise e


@dp.message(Command('girl'))
@raises
async def girl(m: Message):
    "5 pictures from nekosapi(SFW)"

    await reg(m)

    tags: str = "".join(f'&tag={tagsdict[tag]}' for tag in parse_args(m.text))
    lim: int = 5
    urls = (i["image_url"] for i in (await get(f'https://api.nekosapi.com/v3/images/random?rating=safe{tags}&limit={lim}'))["items"])

    media_group = MediaGroupBuilder()
    for i in urls:
        media_group.add_photo(i)

    try:
        await m.answer_media_group(media_group.build())
    except Exception as e:
        print(*urls)
        raise e


@dp.message(Command('girlx'))
@raises
async def explicit(m: Message):
    """
    NSFW pictures
    `/girlx count tag1 tag2`
    """

    await reg(m)

    if m.chat.id not in miha:
        print('Nonadmin tried to what:', m.from_user.id)
        return

    tags: str = "".join(f'&tag={tagsdict[tag]}' for tag in parse_args(m.text))
    lim: int = 5
    pics = (await get(f'https://api.nekosapi.com/v3/images/random?rating=explicit{tags}&limit={lim}'))["items"]
    caption: str = "\n".join(', '.join(j["name"] for j in i["tags"]) for i in pics)

    media_group = MediaGroupBuilder(caption=caption)
    for i in pics:
        media_group.add_photo(i["image_url"])

    try:
        await m.answer_media_group(media_group.build())
    except Exception as e:
        print(*pics)
        raise e

aiorun(dp.start_polling(bot))

with open('count.json', 'w', encoding='utf-8') as f:
    dump(count, f, indent=4)
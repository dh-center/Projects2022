const TelegramApi = require("node-telegram-bot-api");
const{filtersOptions, ColourOptions, WeatherOptions, SentimentOptions, CloudOptions, AnotherColorOption,
    AnotherWeatherOption, AnotherSentimentOption
} = require("./options");
const token = require("/db")

const sequelize = require('./db');
const Models = require("./models/models")
const {where, json, STRING} = require("sequelize");
const {Book_Info} = require("./models/models");
const {verbose} = require("nodemon/lib/config/defaults");


const bot = new TelegramApi(token,{polling:true});


const start = async arrayLike => {
    try {
        await sequelize.authenticate()
        await sequelize.sync()
    } catch (e) {
        console.log("Подключение к бд сломалось:(")
    }


    await bot.setMyCommands([
        {command: '/start', description: 'начальное приветсвие'},
        {command: '/info', description: 'о проекте'},
        {command: '/filters', description: 'фильтры'},
        {command: '/info_filters', description: "о фильтрах"},
        {command: '/read', description: "где почитать книги?"}
    ])

    bot.on('message', async (msg) => {
        const text = msg.text;
        const chatId = msg.chat.id;

        try {
            if (text === '/start') {
                await bot.sendSticker(chatId, "https://tlgrm.ru/_/stickers/4a9/d2e/4a9d2ea3-b927-4caf-8998-b689ab3a59e8/2.webp")
                return bot.sendMessage(chatId, "Добро пожаловать в телеграм бот проекта BookPick")
            }
            if (text === '/info') {
                return bot.sendMessage(chatId, "Наша команда занимается проектами в области цифровых гуманитарных исследований. Сейчас мы работаем над проектом BookPick. Мы считаем, что фильтры, которые используются сейчас для выбора книг однообразные и чаще всего основаны на анализе действий пользователя. Мы предлагаем анализировать не пользователя, а книги, дать возможность читателю по-новому посмотреть на знакомые произведения и сделать свой выбор.На нашем ресурсе можно фильтровать книги по самым часто встречающимся цветам и погоде в тексте, а также общему настроению книги. Для создания фильтров мы используем алгоритмы машинного обучения.Пройди опрос, чтобы улучшить сервис :) https://docs.google.com/forms/d/1kUPTlZfMGbaLCvGKHLPcJBaEcVPWbq6fHtI8EX6MP_0/viewform?edit_requested=true")
            }
            if (text === '/info_filters') {
                return bot.sendMessage(chatId, "Фильтр настроение в книге разработан на основе анализа тональности текста. C помощью этого можно узнать насколько текст положительно или негативно окрашен. Стоит отметить, что этот фильтр не показывает смысловую нагрузку текста, это скорее оценка самим автором событий происходящих в повествовании. Остальные фильтры основаны на методах NLP, это цвета и погода, которые чаще всего попадаются в тексте.")
            }
            if (text === '/read') {
                return bot.sendMessage(chatId, "Книги можно поитать здесь: https://pl.spb.ru")
            }
            if (text === '/filters') {
                await bot.sendMessage(chatId, "Выбери параметры", filtersOptions)
            } else return bot.sendMessage(chatId, "Я тебя не понимаю, попробуй использовать команды")


        } catch (e) {
            return bot.sendMessage(chatId, "Произошла ошибка")
        }
    })


    bot.on('callback_query', async msg => {
        console.log(msg)
        const data = msg.data;
        const chatId = msg.message.chat.id;
        if (data === 'colour') {
            return bot.sendMessage(chatId, "Выбери цвет", ColourOptions)
        }
        if (data === 'weather') {
            return bot.sendMessage(chatId, "Выбери погоду", WeatherOptions)
        }
        if (data === 'sentiment') {
            return bot.sendMessage(chatId, "Выбери настроение", SentimentOptions)
        }
        if (data === 'new') {
            return bot.sendMessage(chatId, "Фильтр еще разрабатывается, выбери что-нибудь другое",filtersOptions)
        }

    });


    bot.on('callback_query', async msg => {
        console.log(msg)
        const data = msg.data;
        const chatId = msg.message.chat.id;

        if (data === 'черный') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    colourId: 3
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, "
                + "где чаще всего встречается черный цвет")
            for (let i = 0; i < 10; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Выбери цвет", AnotherColorOption)
        }

        if (data === 'красный') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    colourId: 1
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего встречается красный цвет")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Выбери цвет", AnotherColorOption)
        }

        if (data === 'белый') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    colourId: 2
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего встречается белый цвет")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другой цвет",AnotherColorOption)
        }
        if (data === 'желтый') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                     colourId: 9
                 }
             });
             const obj_to_json = JSON.stringify(rows)
             const json_books = JSON.parse(obj_to_json)
             await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего встречается желтый цвет")
             for (let i = 0; i < count; i++) {
                 await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
             }
            return bot.sendMessage(chatId, "Можешь выбрать другой цвет",AnotherColorOption)
        }
        if (data === 'синий') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    colourId: 6
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего встречается синий цвет")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другой цвет",AnotherColorOption)
        }
        if (data === 'серый') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    colourId: 4
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего встречается серый цвет")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другой цвет",AnotherColorOption)
        }
        if (data === 'зеленый') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    colourId: 5
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего встречается зеленый цвет")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другой цвет",AnotherColorOption)
        }
        if (data === 'коричневый') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    colourId: 7
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего встречается коричневый цвет")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другой цвет",AnotherColorOption)
        }
        if (data === 'розовый') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    colourId: 9
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего встречается розовый цвет")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другой цвет",AnotherColorOption)
        }
    });

    bot.on('callback_query', async msg => {
        console.log(msg)
        const data = msg.data;
        const chatId = msg.message.chat.id;
        if (data === 'anotherColor') {
            return bot.sendMessage(chatId, "Выбери цвет", ColourOptions)
        }
    });

    bot.on('callback_query', async msg => {
        console.log(msg)
        const data = msg.data;
        const chatId = msg.message.chat.id;

        if (data === 'солнце') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    weatherId: 2
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего солнечно")
            for (let i = 0; i < 10; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другую погоду", AnotherWeatherOption)
        }

        if (data === 'пасмурно') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    weatherId: 1
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего пасмурно")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другую погоду", AnotherWeatherOption)
        }

        if (data === 'мороз') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    weatherId: 3
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего морозная погода")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другую погоду", AnotherWeatherOption)
        }
        if (data === 'Дождь') {
            // const {count, rows} = await Models.Book.findAndCountAll({
            //     where: {
            //         colourId: 2
            //     }
            // });
            // const obj_to_json = JSON.stringify(rows)
            // const json_books = JSON.parse(obj_to_json)
            // await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где чаще всего встречается белый цвет")
            // for (let i = 0; i < count; i++) {
            //     await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            // }
            return bot.sendMessage(chatId, "Команда ещё ищет эту погоду в книге. Можешь выбрать другую",AnotherWeatherOption)
        }

    });

    bot.on('callback_query', async msg => {
        console.log(msg)
        const data = msg.data;
        const chatId = msg.message.chat.id;
        if (data === 'anotherWeather') {
            return bot.sendMessage(chatId, "Выбери погоду", WeatherOptions)
        }
    });

    bot.on('callback_query', async msg => {
        console.log(msg)
        const data = msg.data;
        const chatId = msg.message.chat.id;

        if (data === 'позитив') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    sentimentId: 1
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где преобладает позитивное настроение в тексте")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другое настроение", AnotherSentimentOption)
        }

        if (data === 'негатив') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    sentimentId: 3
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где преобладает грустное настроение в тексте")
            for (let i = 0; i < 10; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другое настроение", AnotherSentimentOption)
        }

        if (data === 'нейтрально') {
            const {count, rows} = await Models.Book.findAndCountAll({
                where: {
                    sentimentId: 2
                }
            });
            const obj_to_json = JSON.stringify(rows)
            const json_books = JSON.parse(obj_to_json)
            await bot.sendMessage(chatId, "Я нашел " + count + " " + "книг, " + "где преобладает нейтральное настроение в тексте")
            for (let i = 0; i < count; i++) {
                await bot.sendMessage(chatId, json_books[i].name + "(" + json_books[i].author + ")")
            }
            return bot.sendMessage(chatId, "Можешь выбрать другое настроение", AnotherSentimentOption)
        }

    });

    bot.on('callback_query', async msg => {
        console.log(msg)
        const data = msg.data;
        const chatId = msg.message.chat.id;
        if (data === 'anotherSentiment') {
            return bot.sendMessage(chatId, "Выбери настроение", SentimentOptions)

        }
    });




}

start()

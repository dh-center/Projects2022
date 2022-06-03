
module.exports = {
    filtersOptions: {
        reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{text: 'Цвет в книге', callback_data:"colour"}],
                    [{text: 'Погода в книге', callback_data:"weather"}],
                    [{text: 'Настроение в книге', callback_data:"sentiment"}],
                    [{text: 'Секретный фильтр', callback_data:"new"}]

                ]
            }
        )
    },

    ColourOptions: {
        reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{text: 'Черный', callback_data:"черный"}],
                    [{text: 'Красный', callback_data:"красный"}],
                    [{text: 'Белый', callback_data:"белый"}],
                    [{text: 'Желтый', callback_data:"желтый"}],
                    [{text: 'Синий', callback_data:"синий"}],
                    [{text: 'Коричневый', callback_data:"коричневый"}],
                    [{text: 'Серый', callback_data:"серый"}],
                    [{text: 'Зеленый', callback_data:"зеленый"}],
                    [{text: 'Розовый', callback_data:"розовый"}]

                ]
            }
        )
    },

    WeatherOptions: {
        reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{text: 'Солнечно', callback_data:"солнце"}],
                    [{text: 'Пасмурно', callback_data:"пасмурно"}],
                    [{text: 'Облачно', callback_data:"облачно"}],
                    [{text: 'Морозно', callback_data:"мороз"}],
                    [{text: 'Дождь', callback_data:"Дождь"}]


                ]
            }
        )
    },
    SentimentOptions: {
        reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{text: 'Позитивно', callback_data:"позитив"}],
                    [{text: 'Грустно', callback_data:"негатив"}]


                ]
            }
        )
    },
    CloudOptions: {
        reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{text: '1', callback_data:"1"}],
                    [{text: '2', callback_data:"2"}],
                    [{text: '3', callback_data:"3"}],
                    [{text: '4', callback_data:"4"}],
                    [{text: '5', callback_data:"5"}],
                    [{text: '6', callback_data:"6"}]


                ]
            }
        )
    },
    AnotherColorOption: {
        reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{text: 'Другой цвет', callback_data:"anotherColor"}]
                ]
            }
        )
    },
    AnotherWeatherOption: {
        reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{text: 'Другая погода', callback_data:"anotherWeather"}]
                ]
            }
        )
    },
    AnotherSentimentOption: {
        reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{text: 'Другое настроение', callback_data:"anotherSentiment"}]
                ]
            }
        )
    }

}



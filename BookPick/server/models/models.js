const sequelize = require("../db")
const{DataTypes} = require('sequelize')

const User = sequelize.define('user', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
    email:{type: DataTypes.STRING, unique: true},
    password:{type:DataTypes.STRING},
    role:{type:DataTypes.STRING, defaultValue:"USER"},
})

const Basket = sequelize.define('basket', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true}
})

const Basket_Book = sequelize.define('basket_book', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true}
})

const Book = sequelize.define('book', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
    name:{type: DataTypes.STRING, unique: true,allowNull:false},
    author:{type:DataTypes.STRING, allowNull:false},
    img:{type:DataTypes.STRING, allowNull:false}
})

const Genre = sequelize.define('genre', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
    name:{type:DataTypes.STRING, unique: true,allowNull:false}
})

const Time = sequelize.define('time', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
    name:{type:DataTypes.STRING, unique: true,allowNull:false}
})

const Age  = sequelize.define('age', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
    name:{type:DataTypes.INTEGER, allowNull:false}
})

const Colour = sequelize.define('colour', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
    name:{type:DataTypes.STRING, unique: true,allowNull:false}
})
const Sentiment = sequelize.define('sentiment', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
    name:{type:DataTypes.STRING, unique: true,allowNull:false}
})
const Weather= sequelize.define('weather', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
    name:{type:DataTypes.STRING, unique: true,allowNull:false}
})

const Book_Info = sequelize.define('book_info', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
    title:{type:DataTypes.STRING,allowNull:false},
    description:{type:DataTypes.STRING,allowNull:false}
})

const GenreTime = sequelize.define('genre_time', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const GenreAge = sequelize.define('genre_age', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const AgeTime = sequelize.define('age_time', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const ColourGenre = sequelize.define('colour_genre', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const ColourTime = sequelize.define('colour_time', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const ColourAge = sequelize.define('colour_age', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const SentimentGenre = sequelize.define('sentiment_genre', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const SentimentTime = sequelize.define('sentiment_time', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const SentimentAge = sequelize.define('sentiment_age', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const WeatherGenre = sequelize.define('weather_genre', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const WeatherTime = sequelize.define('weather_time', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const WeatherAge = sequelize.define('weather_age', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const ColourSentiment = sequelize.define('colour_sentiment', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const ColourWeather = sequelize.define('colour_weather', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})

const SentimentWeather = sequelize.define('sentiment_weather', {
    id:{type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true},
})


User.hasOne(Basket)
Basket.belongsTo(User)

Basket.hasMany(Basket_Book)
Basket_Book.belongsTo(Basket)

Book.hasMany(Basket_Book)
Basket_Book.belongsTo(Book)

Book.hasMany(Book_Info,{as: 'info'})
Book_Info.belongsTo(Book)

Genre.hasMany(Book)
Book.belongsTo(Genre)

Time.hasMany(Book)
Book.belongsTo(Time)

Age.hasMany(Book)
Book.belongsTo(Age)

Colour.hasMany(Book)
Book.belongsTo(Colour)

Sentiment.hasMany(Book)
Book.belongsTo(Sentiment)

Weather.hasMany(Book)
Book.belongsTo(Weather)




Genre.belongsToMany(Time,{through: GenreTime })
Time.belongsToMany(Genre,{through: GenreTime })

Age.belongsToMany(Genre, {through: GenreAge })
Genre.belongsToMany(Age, {through: GenreAge })

Age.belongsToMany(Time, {through: AgeTime })
Time.belongsToMany(Age, {through: AgeTime })



Colour.belongsToMany(Genre,{through: ColourGenre })
Genre.belongsToMany(Colour,{through: ColourGenre })

Age.belongsToMany(Colour, {through: ColourAge })
Colour.belongsToMany(Age, {through: ColourAge })

Colour.belongsToMany(Time, {through: ColourTime })
Time.belongsToMany(Colour, {through: ColourTime })


Sentiment.belongsToMany(Genre,{through: SentimentGenre })
Genre.belongsToMany(Sentiment,{through: SentimentGenre })

Age.belongsToMany(Sentiment, {through: SentimentAge })
Sentiment.belongsToMany(Age, {through: SentimentAge })

Sentiment.belongsToMany(Time, {through: SentimentTime })
Time.belongsToMany(Sentiment, {through: SentimentTime })


Weather.belongsToMany(Genre,{through: WeatherGenre })
Genre.belongsToMany(Sentiment,{through: WeatherGenre })

Age.belongsToMany(Weather, {through: WeatherAge })
Weather.belongsToMany(Age, {through: WeatherAge })

Weather.belongsToMany(Time, {through: WeatherTime })
Time.belongsToMany(Weather, {through: WeatherTime })



Sentiment.belongsToMany(Colour,{through: ColourSentiment })
Colour.belongsToMany(Sentiment,{through: ColourSentiment })

Colour.belongsToMany(Weather, {through: ColourWeather })
Weather.belongsToMany(Colour, {through: ColourWeather})

Sentiment.belongsToMany(Weather, {through: SentimentWeather })
Weather.belongsToMany(Sentiment, {through: SentimentWeather })

module.exports = {
    User,Basket, Basket_Book, Book, Genre, Time, Age, Colour, Sentiment, Weather, GenreAge, GenreTime, AgeTime, ColourGenre, ColourAge, ColourTime, SentimentGenre, SentimentTime, SentimentAge, WeatherGenre, WeatherTime, WeatherAge, ColourSentiment, ColourWeather, SentimentWeather,Book_Info,
}

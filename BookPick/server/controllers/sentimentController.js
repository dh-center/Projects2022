const{Sentiment} = require('../models/models')
const ApiError = require('../error/ApiError');

class SentimentController{
    async create(req,res){
        const{name} = req.body
        const sentiment = await Sentiment.create({name})
        return res.json(sentiment)


    }

    async getAll(req,res){
        const sentiments = await Sentiment.findAll()
        return res.json(sentiments)

    }

}

module.exports = new SentimentController()
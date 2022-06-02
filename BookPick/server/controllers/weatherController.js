const{Weather} = require('../models/models')
const ApiError = require('../error/ApiError');

class WeatherController{
    async create(req,res){
        const{name} = req.body
        const weather = await Weather.create({name})
        return res.json(weather)


    }

    async getAll(req,res){
        const weathers = await Weather.findAll()
        return res.json(weathers)

    }

}

module.exports = new WeatherController()
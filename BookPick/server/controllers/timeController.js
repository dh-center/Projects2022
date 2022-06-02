const {Time} = require("../models/models");
const ApiError = require('../error/ApiError')

class TimeController{
    async create(req,res){
        const{name} = req.body
        const time = await Time.create({name})
        return res.json(time)
    }

    async getAll(req,res){
        const times = await Time.findAll()
        return res.json(times)
    }

}

module.exports = new TimeController()
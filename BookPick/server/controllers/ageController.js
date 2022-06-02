const {Age} = require("../models/models");
const ApiError = require('../error/ApiError')

class AgeController{
    async create(req, res){
        const{name} = req.body
        const age = await Age.create({name})
        return res.json(age)
    }

    async getAll(req,res){
        const ages = await Age.findAll()
        return res.json(ages)
    }

}

module.exports = new AgeController()
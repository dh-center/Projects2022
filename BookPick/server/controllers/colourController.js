const{Colour} = require('../models/models')
const ApiError = require('../error/ApiError');

class ColourController{
    async create(req,res){
        const{name} = req.body
        const colour = await Colour.create({name})
        return res.json(colour)


    }

    async getAll(req,res){
        const colours = await Colour.findAll()
        return res.json(colours)

    }

}

module.exports = new ColourController()
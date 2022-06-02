const uuid = require('uuid')
const path = require('path');
const {Book, Book_Info} = require('../models/models')
const ApiError = require('../error/ApiError')
class BookController{
    async create(req,res,next){
        try{
            let {name, author, genreId, timeId, ageId, colourId, sentimentId, weatherId, info} = req.body
            const {img} = req.files
            let fileName = uuid.v4() + ".jpg"
            await img.mv(path.resolve(__dirname, '..', 'static', fileName))//адаптирует путь к файлу аод операционную систему
            const book = await Book.create({name, author, genreId, timeId, ageId, colourId, sentimentId, weatherId, img:fileName})

            if (info) {
                info = JSON.parse(info)
                info.forEach(i =>
                    Book_Info.create({
                        title: i.title,
                        description: i.description,
                        bookId: book.id
                    }))
            }

            return res.json(book)

        }catch (e){
            next(ApiError.badRequest(e.massage))
        }


    }

    async getAll(req,res){
        let { genreId, timeId, ageId, colourId, sentimentId, weatherId} = req.query
        let books;
        //не выбран фильтр или выбраны все
        if (!genreId && !timeId && !ageId && !colourId && !sentimentId && !weatherId) {
            books = await Book.findAll()
        }
        if (genreId && timeId && ageId && colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId,timeId,ageId,colourId, sentimentId, weatherId}})
        }

        //выбран только один фильтр
        if (genreId && !timeId && !ageId && !colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId}})
        }
        if (!genreId && timeId && !ageId && !colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{timeId}})
        }
        if (!genreId && !timeId && ageId && !colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{ageId}})
        }
        if (!genreId && !timeId && !ageId && colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{colourId}})
        }
        if (!genreId && !timeId && !ageId && !colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{sentimentId}})
        }
        if (!genreId && !timeId && !ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{weatherId}})
        }

        //выбраны 2 фильтра
        //классические
        if (genreId && timeId && !ageId && !colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId, timeId}})

        }
        if (genreId && !timeId && ageId && !colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId, ageId}})

        }
        if (!genreId && timeId && ageId && !colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{ageId, timeId}})

        }
        //классические + нлп
        if (genreId && !timeId && !ageId && colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId, colourId}})

        }
        if (genreId && !timeId && !ageId && !colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId, sentimentId}})

        }
        if (genreId && !timeId && !ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, weatherId}})

        }

        if (!genreId && timeId && !ageId && colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{timeId, colourId}})

        }
        if (!genreId && timeId && !ageId && !colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{timeId, sentimentId}})

        }
        if (!genreId && timeId && !ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{timeId, weatherId}})

        }

        if (!genreId && !timeId && ageId && colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{ageId, colourId}})

        }
        if (!genreId && !timeId && ageId && !colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{ageId, sentimentId}})

        }
        if (!genreId && !timeId && ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{ageId, weatherId}})

        }
        //нлп фильтры
        if (!genreId && !timeId && !ageId && colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{colourId, sentimentId}})

        }
        if (!genreId && !timeId && !ageId && colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{colourId, weatherId}})

        }
        if (!genreId && !timeId && !ageId && !colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{sentimentId, weatherId}})
        }
        //выбраны 3 фильтра
        // классические
        if (genreId && timeId && ageId && !colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId, ageId, timeId}})

        }
        if (!genreId && !timeId && !ageId && colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{colourId, sentimentId, weatherId}})

        }
        //выбраны один из классических и 2 из нлп
        if (genreId && !timeId && !ageId && colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId, colourId, sentimentId}})

        }
        if (genreId && !timeId && !ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, colourId, weatherId}})

        }
        if (genreId && !timeId && !ageId && !colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, sentimentId, weatherId}})

        }

        if (!genreId && timeId && !ageId && colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{timeId, colourId, sentimentId}})

        }
        if (!genreId && timeId && !ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{timeId, colourId, weatherId}})

        }
        if (!genreId && timeId && !ageId && !colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{timeId, sentimentId, weatherId}})

        }

        if (!genreId && !timeId && ageId && colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{ageId, colourId, sentimentId}})

        }
        if (!genreId && !timeId && ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{ageId, colourId, weatherId}})

        }
        if (!genreId && !timeId && ageId && !colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{ageId, sentimentId, weatherId}})

        }

        //выбраны 2 из классических и 1 из нлп

        if (genreId && timeId && !ageId && colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{colourId, genreId, timeId}})

        }
        if (genreId && !timeId && ageId && colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{colourId, genreId, ageId}})

        }
        if (!genreId && timeId && ageId && colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{colourId, ageId, timeId}})

        }

        if (genreId && timeId && !ageId && !colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{sentimentId, genreId, timeId}})

        }
        if (genreId && !timeId && ageId && !colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{sentimentId, genreId, ageId}})

        }
        if (!genreId && timeId && ageId && !colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{sentimentId, ageId, timeId}})

        }

        if (genreId && timeId && !ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{weatherId, genreId, timeId}})

        }
        if (genreId && !timeId && ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{weatherId, genreId, ageId}})

        }
        if (!genreId && timeId && ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{weatherId, ageId, timeId}})

        }

        //выбраны 4 фильтра
        //выбраны 3 из классических и 1 из нлп
        if (genreId && timeId && ageId && colourId && !sentimentId && !weatherId) {
            books = await Book.findAll({where:{colourId, genreId, timeId,ageId}})

        }
        if (genreId && timeId && ageId && !colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{sentimentId, genreId, timeId,ageId}})

        }
        if (genreId && timeId && ageId && !colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{weatherId, genreId, timeId,ageId}})

        }
        //выбраны 1 из классических и 3 из нлп
        if (genreId && !timeId && !ageId && colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, colourId, sentimentId, weatherId }})

        }
        if (!genreId && timeId && !ageId && colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{timeId, colourId, sentimentId, weatherId }})

        }
        if (!genreId && !timeId && ageId && colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{ageId, colourId, sentimentId, weatherId }})

        }
        //выбраны 2 из классических и 2 из нлп
        if (genreId && !timeId && ageId && colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId, ageId, colourId, sentimentId }})

        }
        if (genreId && !timeId && ageId && colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, ageId, colourId, weatherId }})

        }
        if (genreId && !timeId && ageId && !colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, ageId, sentimentId, weatherId }})

        }
        if (genreId && timeId && !ageId && colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId, timeId, colourId, sentimentId }})

        }
        if (genreId && timeId && !ageId && colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, timeId, colourId, weatherId }})

        }
        if (genreId && timeId && !ageId && !colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, timeId, sentimentId, weatherId }})

        }
        if (!genreId && timeId && ageId && colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{ageId, timeId, colourId, sentimentId }})

        }
        if (!genreId && timeId && ageId && colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{ageId, timeId, colourId, weatherId }})

        }
        if (!genreId && timeId && ageId && !colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{ageId, timeId, sentimentId, weatherId }})

        }
        //выбраны 5 фильтра
        //2 из классических 3 из нлп
        if (genreId && !timeId && ageId && colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, ageId, colourId, sentimentId,weatherId }})

        }
        if (genreId && timeId && !ageId && colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, timeId, colourId, weatherId, sentimentId }})

        }
        if (!genreId && timeId && ageId && !colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{timeId, ageId, colourId, weatherId, sentimentId }})

        }
        //3 из классических 2 из нлп
        if (genreId && timeId && ageId && colourId && sentimentId && !weatherId) {
            books = await Book.findAll({where:{genreId, timeId, ageId, colourId, sentimentId }})

        }
        if (genreId && timeId && ageId && colourId && !sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, timeId, ageId,  colourId, weatherId }})

        }
        if (genreId && timeId && ageId && !colourId && sentimentId && weatherId) {
            books = await Book.findAll({where:{genreId, timeId, ageId, sentimentId, weatherId }})
        }

        return res.json(books)

    }

    async getOne(req,res){
        const{id} = req.params
        const book = await Book.findOne(
            {
                where: {id},
                include: [{model:Book_Info, as: 'info'}]

            },

        )
        return res.json(book)

    }
}

module.exports = new BookController()
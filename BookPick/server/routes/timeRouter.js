const Router = require("express")
const router = new Router()
const timeController = require("../controllers/timeController")


router.post("/",timeController.create)
router.get("/",timeController.getAll)


module.exports = router
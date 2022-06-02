const Router = require("express")
const router = new Router()
const weatherController = require("../controllers/weatherController")

router.post("/",weatherController.create)
router.get("/",weatherController.getAll)


module.exports = router
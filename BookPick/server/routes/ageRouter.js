const Router = require("express")
const router = new Router()
const ageController = require("../controllers/ageController")

router.post("/",ageController.create)
router.get("/",ageController.getAll)


module.exports = router
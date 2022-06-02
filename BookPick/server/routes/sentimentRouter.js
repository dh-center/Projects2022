const Router = require("express")
const router = new Router()
const sentimentController = require("../controllers/sentimentController")

router.post("/",sentimentController.create)
router.get("/",sentimentController.getAll)


module.exports = router
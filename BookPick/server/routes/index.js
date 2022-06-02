const Router = require("express")
const router = new Router()
const bookRouter = require("./bookRouter")
const genreRouter = require("./genreRouter")
const timeRouter = require("./timeRouter")
const ageRouter = require("./ageRouter")
const userRouter = require("./userRouter")
const colourRouter = require("./colourRouter")
const sentimentRouter = require("./sentimentRouter")
const weatherRouter = require("./weatherRouter")

router.use("/user", userRouter)
router.use("/time", timeRouter)
router.use("/genre", genreRouter)
router.use("/age", ageRouter)
router.use("/book", bookRouter)
router.use("/colour", colourRouter)
router.use("/sentiment", sentimentRouter)
router.use("/weather", weatherRouter)


module.exports = router
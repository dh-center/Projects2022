const Router = require("express")
const router = new Router()
const userController = require("../controllers/userController")
const authMiddleware = require("../middleware/authMiddleware")
//const path = require("path");

router.post("/registration", userController.registration)//регистрация
router.post("/login",userController.login)//вход
router.get( "/auth",authMiddleware, userController.check)//проверка зарегистрирован ли пользователь по gvt токену


module.exports = router
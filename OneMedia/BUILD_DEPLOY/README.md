## BUILD_DEPLOY

Данный каталог содержит все необходимые инструкции в формате [Dockerfile](https://docs.docker.com/engine/reference/builder/#:~:text=A%20Dockerfile%20is%20a%20text,command%2Dline%20instructions%20in%20succession.), для запуска каждого из компонентов системы.

Также в данном каталоге должен находиться файл .env, в котором необходимо определить пользовательские переменные.

[Пример файла .env](.example_env)

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postres_password
POSTGRES_HOST=database
# Tlg extractor and bot
api_id=id_number
api_hash=api_hash
api_phone=+79000000001
# bot
bot_token=bot_token
# monitoring bot
monitoring_bot_token=monitoting_token
# vk
vk_phones=+7900000001,+79000000002,+79000000003
vk_passwords=account_password1,account_password2,account_password3
# api_calls_bot_tokens
api_calls_bot_tokens=bot_toker
# search
SEARCH_HOST=test_search
# ui
IP_PORT_DATABASE=127.0.0.1:5432
# grafana
GF_SECURITY_ADMIN_USER=test_user
GF_SECURITY_ADMIN_PASSWORD=test_password
```
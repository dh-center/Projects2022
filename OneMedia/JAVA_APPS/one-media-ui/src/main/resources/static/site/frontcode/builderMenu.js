const axios = require('axios');

let builderMenu =  {
    template: '\
    <nav class="navbar navbar-default navbar-trans navbar-expand-lg fixed-top">\
        <div class="container">\
            <button class="navbar-toggler collapsed" type="button" data-toggle="collapse" data-target="#navbarDefault"\
                    aria-controls="navbarDefault" aria-expanded="false" aria-label="Toggle navigation">\
                <span></span>\
                <span></span>\
                <span></span>\
            </button>\
            <a class="navbar-brand text-brand" href="index.html">ONE <span class="color-b">MEDIA</span></a>\
            <div class="navbar-collapse collapse justify-content-center" id="navbarDefault">\
                <ul class="navbar-nav">\
                    <li class="nav-item" style="padding-right: 1rem;">\
                        <a class="nav-link" id="anchor-to-about" href="/">About</a>\
                    </li>\
                    <li class="nav-item dropdown" style="padding-right: 1rem;">\
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button"\
                           data-toggle="dropdown"\
                           aria-haspopup="true" aria-expanded="false">\
                            Resources\
                        </a>\
                        <div class="dropdown-menu" aria-labelledby="navbarDropdown">\
                            <a class="dropdown-item" href="media.html">Media Analysis</a>\
                            <a class="dropdown-item" href="free-api.html">Open/Free API</a>\
                            <a class="dropdown-item" href="tutorial.html">How to use?</a>\
                            <a class="dropdown-item" href="contribution.html">Contribution</a>\
                        </div>\
                    </li>\
                    <li class="nav-item">\
                        <a class="nav-link" href="work.html" style="padding-right: 1rem;">Service</a>\
                    </li>\
                    <li class="nav-item">\
                        <a class="nav-link" href="media.html#contactsInfo" style="padding-right: 1rem;">Contacts</a>\
                    </li>\
                    <li class="nav-item d-xl-none">\
                        <a class="nav-link" href="login.html" style="padding-right: 1rem;">Sign in</a>\
                    </li>\
                </ul>\
            </div>\
            <button style="border-radius: 10px" type="button" class="btn btn-b-n nav-search navbar-toggle-box-collapse d-xl-none"\
                    data-toggle="collapse"\
                    data-target="#navbarTogglerDemo01" aria-expanded="false">\
                <span class="fa fa-plus-circle" aria-hidden="true"></span>\
            </button>\
            <button v-bind:style="{ \'border-radius\': getBorderRadius() }" type="button" class="btn btn-lg btn-b-n navbar-toggle-box-collapse d-none d-xl-block"\
                    onclick="window.location.href=\'media.html#contactsMail\'"\
                    data-toggle="collapse"\
                    data-target="#navbarTogglerDemo01" aria-expanded="false">\
                <span class="fa fa-plus" aria-hidden="true"></span>\
                Join Us\
            </button>\
            <button v-if="!isAuth && !isLoginPage" type="button" class="btn btn-lg btn-b-n navbar-toggle-box-collapse d-none d-xl-block"\
                    onclick="window.location.href=\'login.html\'"\
                    data-toggle="collapse"\
                    data-target="#navbarTogglerDemo01" aria-expanded="false" style="border-left: 1px solid rgba(255,0,0,0.09); border-radius: 0px 20px 20px 0px">\
                <span class="fas fa-sign-in-alt" aria-hidden="true"></span>\
                Sign in\
            </button>\
            <form v-if="isAuth" action="/logout" method="post">\
                <button  type="submit" class="btn btn-lg btn-b-n navbar-toggle-box-collapse d-none d-xl-block"\
                        data-toggle="collapse"\
                        data-target="#navbarTogglerDemo01" aria-expanded="false" style="border-left: 1px solid rgba(255,0,0,0.09); border-radius: 0px 20px 20px 0px">\
                        <span class="fas fa-sign-out-alt" aria-hidden="true"></span>\
                    Sign out\
                </button>\
            </form>\
        </div>\
    </nav>\
    ',

    data () {
        return {
            isAuth: false,
            isLoginPage: false
        }
    },

    created : function () {
        axios({
            method: 'get',
            url: '/auth/isAuthenticated',
        }).then(function (response) {
            this.isAuth = response.data
            console.log(response.data);
        }.bind(this));

        this.isLoginPage = location.href.includes("login.html")
        console.log("builderMenu created!");
    },

    methods: {
        getBorderRadius: function (){
            if (this.isLoginPage){
                return "10px 10px 10px 10px";
            }
            return "10px 0px 0px 10px";
        }
    }
};


export {builderMenu};

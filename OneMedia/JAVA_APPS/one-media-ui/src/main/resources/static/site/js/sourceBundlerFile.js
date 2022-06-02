import Vue from 'vue';
import {builderMenu} from "../frontcode/builderMenu";
import {toggleFun} from "../frontcode/listToggler";

// window.onload = function() {
    if ( $( '#head' ).length ) { // initialise head menu
        Vue.component("builder-menu", builderMenu);
        let app = new Vue(
            { el: '#head' });
        console.log("builderMenu loaded "+builderMenu);
    }

    toggleFun();
// };



// checking that npm works

import _ from 'lodash';
console.log(_.join(['Hello', 'webpack'], ' '));

for (var i = 0; i< 10; i++){
    console.log(i);
}
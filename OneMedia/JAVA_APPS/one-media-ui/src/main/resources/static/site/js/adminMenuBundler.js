import Vue from 'vue';
import {adminMenu} from "../frontcode/adminMenu";
import {adminEntry} from "../frontcode/adminEntry";
import {projectSwitcher} from "../frontcode/projectSwitcher";
import {workUpdater} from "../frontcode/workUpdater";


Vue.component("admin-entry", adminEntry);
Vue.component("project-switcher", projectSwitcher);
Vue.component("work-updater", workUpdater);
Vue.component("admin-menu", adminMenu);

let app = new Vue({el: '#app'});

console.log("admin-menu loaded " + adminMenu);


var showdown  = require('showdown');


showdown.setFlavor('vanilla');
let converter = new showdown.Converter();


let searchResult = {
    props: {
        newsItem: Object
    },

    template: '\
    <div class ="card" style = "margin-top: 20px; border-width: 0px" >\
        <div class="card-header" style="background-color:  rgba(232, 203, 203, 0.53)" v-on:click="toggleDesc = !toggleDesc">\
            {{newsItem.source}} : {{newsItem.channelName}}\
            <a v-if="showExpand(newsItem) & toggleDesc == false" class="toggle-expand">&#x25BC;</a>\
            <a v-if="showExpand(newsItem) & toggleDesc == true" class="toggle-expand">&#x25B2;</a>\
        </div>\
        <div class="card-body my-card-body">\
              <h5 class="card-title"> {{newsItem.channelTitle}}</h5>\
              <div v-if="newsItem.imageLink.length !== 0 & showExpand(newsItem) & toggleDesc == true">\
                <hr>\
                <img :src="newsItem.imageLink"  width="55%" alt="Italian Trulli">\
                <hr>\
              </div>\
              <div class="card-text" style="white-space: pre-line;" v-html="getDescription(newsItem)"></div>\
              <div v-if="newsItem.link.length !== 0">\
                 <hr>\
                 <a v-bind:href="newsItem.link" class="on-hover-outbound btn btn-primary my-btn-one" target="_blank">Visit</a>\
                 <a> &nbsp; &nbsp; <span style="font-weight: bold;">URL</span>: &nbsp; {{newsItem.link}}</a>\
              </div>\
        </div>\
    </div>\
',

    data: function (){
        return {
            toggleDesc: false
        }
    },

    methods: {

        getImageLink: function (){
            return this.newsItem.imageLink.split(",")[0];
        },

        getDescription : function (newsItem) {
            if (this.toggleDesc || newsItem.content.length <= 320) {
                return converter.makeHtml(newsItem.content);
            }
            return converter.makeHtml(newsItem.content.substr(0,300) + "...");
        },

        showExpand: function (newsItem) {
            return newsItem.content.length > 320;
        }
    }

};


export {searchResult};
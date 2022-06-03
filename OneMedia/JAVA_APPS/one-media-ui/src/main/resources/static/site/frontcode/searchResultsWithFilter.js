let searchResultsWithFilter = {
    template: '\
    <div class="row searchcontainer" v-if="listToShowFiltered.length !== 0" style="margin-top: 30px;">\
        <navbar-result @emitFilterNavBar="emitFilterNavBar" v-bind:searchFieldResults="listToShowFiltered.length"></navbar-result>\
        <div :key="searchIndex">\
            <search-result v-for="item in listToShowFiltered" v-bind:key="item.channelId + item.messageId" v-bind:newsItem="item"></search-result>\
        </div>\
    </div>\
    ',

    data: function () {
        return {
            listToShowFiltered: this.newsArray,
            listToShow: this.newsArray,
            currentFilter: {
                filteredText: ''
            },
            searchIndex: 1
        }
    },

    props: {
        newsArray: {
            type: Array,
            default: () => []
        },
        chosenPlatforms: {
            type: Array,
            default: () => []
        },
    },

    watch: {
        chosenPlatforms: function (val) {
            this.emitFilterNavBar(this.currentFilter);
        },

        newsArray: function (val) {
            this.emitFilterNavBar(this.currentFilter);
        },
    },

    methods: {
        emitFilterNavBar: function (filter) {
            console.log(filter);
            this.currentFilter = filter;
            let query = filter.filteredText.toLowerCase();

            if (query.length === 0) {
                this.listToShowFiltered = this.listToShow;
            } else {
                this.listToShowFiltered = this.listToShow.filter((item) => this.toStringItem(item).indexOf(query) !== -1);
            }

            if (this.chosenPlatforms.length !== 0) {
                this.listToShowFiltered = this.listToShowFiltered.filter((item) => this.chosenPlatforms.indexOf(item.source) !== -1);
            }

            this.searchIndex += 1;
        },

        toStringItem: function (item) {
            return (item.content + " " + item.channelTitle + " " + item.channelName).toLowerCase();
        },

    }
}

export {searchResultsWithFilter};
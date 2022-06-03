const axios = require("axios");
let sourceFilter = {
    template: "\
            <div>\
                <select v-show=\"isLoaded && !isTooBroad\" v-bind:id=\"getId()\" multiple=\"multiple\"></select>\
                <span v-if=\"!isLoaded && !isTooBroad\" class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span>\
                <span v-if=\"!isLoaded && isTooBroad\" style=\"color: #500000\" v-on:click='refresh()'>TOO BROAD &#x21bb;</span>\
            </div>\
    ",

    props: {
        title: {
            type: String,
            default: "Choose"
        },
        query: {
            type: String,
            default: "{}"
        },
        name: {
            type: String,
            default: ""
        },
        preSelected: {
            type: Array,
            default: () => []
        },
        type: {
            type: String,
            default: ""
        },
        jwt: {
            type: String
        }
    },

    data: function () {
        return {
            isLoaded: false,
            isTooBroad: false,
            platforms: [],
            sources: [],
            chosen: [],
            data: []
        }
    },

    mounted: function () {
        this.refresh();
    },

    watch: {
        type: function (oldV, newV) {
            this.renderSelect();
        }
    },

    methods: {

        refresh: function () {
            let query = JSON.parse(this.query);
            if (!query.hasOwnProperty("must_terms") || query.must_terms.length === 0) {
                this.isTooBroad = true;
            } else {
                this.isTooBroad = false;
                this.loadAll(query);
            }
        },

        getId: function () {
            return "sources-vs-platform" + this.name.hashCode();
        },

        loadAll: function (queryToRead) {
            let query = {
                enrich_content: false,
                number_of_best_hits: 50000
            };

            let termsMap = function (terms) {
                return {
                    synonyms: terms
                }
            };

            query.contentDocTermsMust = queryToRead.must_terms.map(termsMap);
            query.contentDocTermsShould = queryToRead.should_terms.map(termsMap);
            query.contentDocTermsExcluded = queryToRead.excluded_terms.map(termsMap);

            axios({
                method: 'post',
                url: 'http://54.36.174.129:8083/search_old',
                headers: {'X-One-Media': this.jwt},
                data: query,
            }).then(function (response) {
                this.data = response.data;
                this.renderSelect();
            }.bind(this));
        },

        renderSelect: function () {
            let optsources = [];
            let news = this.data;
            let platforms = news.map((it) => it.source).filter((value, index, self) => {
                return self.indexOf(value) === index
            });
            let sources = [];
            let used = [];
            for (let i = 0; i < platforms.length; i++) {
                sources[platforms[i]] = [];
                used[platforms[i]] = {}
            }
            for (let i = 0; i < news.length; i++) {
                let item = news[i];
                if (item.channelName in used[item.source]) {
                    used[item.source][item.channelName].count++;
                } else {
                    used[item.source][item.channelName] = {
                        channelName: item.channelName,
                        channelTitle: item.channelTitle,
                        source: item.source,
                        selected: false,
                        count: 1
                    };
                }
            }

            for (let i = 0; i < this.preSelected.length; i++) {
                let item = this.preSelected[i];
                if (item[0] in used) {
                    if (item[1] in used[item[0]]) {
                        used[item[0]][item[1]].selected = true;
                    }
                }
            }

            let countAll = 0;
            for (let i = 0; i < platforms.length; i++) {
                let iterated = used[platforms[i]];
                for (let channel in iterated) {
                    sources[platforms[i]].push(iterated[channel]);
                }
                countAll += Object.keys(iterated).length;
            }

            if (countAll > 9000) {
                this.isTooBroad = true;
                return;
            }

            for (let i = 0; i < platforms.length; i++) {
                sources[platforms[i]].sort((item, item1) => item1.count - item.count);
            }

            $(document).ready(function () {
                for (let i = 0; i < platforms.length; i++) {
                    let group = sources[platforms[i]];
                    if (group.length !== 0) {
                        let optgroup = {};
                        optgroup.label = platforms[i];
                        optgroup.children = [];

                        for (let j = 0; j < group.length; j++) {
                            let item = group[j];
                            let label = '';
                            if (item.channelName === item.channelTitle) {
                                label = item.channelName;
                            } else {
                                label = item.channelName + ' : ' + item.channelTitle;
                            }
                            label += ' #' + item.count;
                            optgroup.children.push({
                                label: label,
                                value: item.source + " : " + item.channelName,
                                selected: item.selected,
                            })
                        }
                        optsources.push(optgroup);
                    }
                }

                let selector = $("#" + this.getId());
                selector.multiselect({
                    enableClickableOptGroups: true,
                    buttonText: function (options, select) {
                        return this.title + ' ▼';
                    }.bind(this),
                    buttonTitle: function (options, select) {
                        return 'Platforms TLG,WEB,VK';
                    },
                    onDropdownShow: function (event) {
                        $("#" + this.getId()).siblings().first().find("span.multiselect-selected-text").text(this.title + ' ▲');
                    }.bind(this),
                    onDropdownHide: function (event) {
                        $("#" + this.getId()).siblings().first().find("span.multiselect-selected-text").text(this.title + ' ▼');
                    }.bind(this),
                    onChange: function (option, checked, select) {
                        if (Array.isArray(option)) {
                            for (let i = 0; i < option.length; i++) {
                                let channelName = $(option[i]).attr("label").split(' : ')[0].split(' #')[0];
                                let source = $(option[i]).val().split(' : ')[0];
                                this.enrichChosen(source, channelName, checked);
                            }
                        } else {
                            let channelName = $(option).attr("label").split(' : ')[0].split(' #')[0];
                            let source = $(option).val().split(' : ')[0];
                            this.enrichChosen(source, channelName, checked);
                        }
                    }.bind(this),
                    onSelectAll: function () {
                        alert('onSelectAll triggered!');
                    },
                    enableFiltering: true,
                    dropRight: true,
                    maxHeight: 400,
                    enableCaseInsensitiveFiltering: true,
                    enableCollapsibleOptGroups: true,
                    collapseOptGroupsByDefault: true,
                    multiple: true
                });
                selector.multiselect('dataprovider', optsources);
                this.isLoaded = true;
            }.bind(this))
            this.chosen = this.preSelected;
        },

        emitFilter: function () {
            this.$emit("emitChosenFilter", {
                chosenSources: this.chosen
            });
        },

        enrichChosen: function (source, channel_name, selected) {
            if (selected) {
                this.addToChosen(source, channel_name);
            } else {
                this.removeFromChosen(source, channel_name);
            }
            this.emitFilter();
        },

        addToChosen: function (source, channel) {
            if (this.chosen.map(it => it[1] + ":|:" + it[0]).indexOf(channel + ":|:" + source) === -1) {
                this.chosen.push([source, channel])
            }
        },

        removeFromChosen: function (source, channel) {
            let index = this.chosen.map(it => it[1] + ":|:" + it[0]).indexOf(channel + ":|:" + source);
            if (index !== -1) {
                this.chosen.splice(index, 1);
            }
        }
    }
};


export {sourceFilter}
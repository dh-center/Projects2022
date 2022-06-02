let filterRunTimePicker = {
    template: "\
    <div class='container'>\
        <div class='row' style='margin-top: 30px'>\
            <div class='col-sm-auto'>\
                Platform Filter : \
            </div>\
            <transition name=\"fade\">\
                <div v-show='isLoaded' class='col-sm-auto'>\
                    <select id=\"example-multiple-selected\" multiple=\"multiple\"></select>\
                </div>\
            </transition>\
        </div>\
    </div>\
    ",

    props: {
        news: {
            type: Array,
            default: []
        }
    },

    data: function () {
        return {
            isLoaded: false,
            platforms: [],
            sources: [],
            exclusions: []
        }
    },

    mounted: function () {
        let platforms = this.news.map((it) => it.source).filter((value, index, self) => {   return self.indexOf(value) === index });

        let sources = [];
        let used = [];
        for (let i = 0; i < platforms.length; i++) {
            sources[platforms[i]] = [];
            used[platforms[i]] = {}
        }
        for (let i = 0; i < this.news.length; i++) {
            let item = this.news[i];
            if (item.channelName in used[item.source]) {
                used[item.source][item.channelName].count++;
            } else {
                used[item.source][item.channelName] = {
                    channelName: item.channelName,
                    channelTitle: item.channelTitle,
                    source: item.source,
                    count: 1
                };
            }
        }

        for (let i = 0; i < platforms.length; i++) {
            let iterated = used[platforms[i]];
            for (let channel in iterated) {
                sources[platforms[i]].push(iterated[channel]);
            }
        }

        for (let i = 0; i < platforms.length; i++) {
            sources[platforms[i]].sort((item, item1) => item1.count - item.count);
        }

        this.sources = sources;
        this.platforms = platforms;

        $(document).ready(function () {
            let optsources = [];

            for (let i = 0; i < this.platforms.length; i++) {
                let group = this.sources[this.platforms[i]];
                if (group.length !== 0) {
                    let optgroup = {};
                    optgroup.label = this.platforms[i];
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
                            selected: true,
                        })
                    }
                    optsources.push(optgroup);
                }
            }
            // var optgroups = [
            //     {
            //         label: 'Group 1', children: [
            //             {label: 'Option 1.1', value: '1-1', selected: true},
            //             {label: 'Option 1.2', value: '1-2'},
            //             {label: 'Option 1.3', value: '1-3'}
            //         ]
            //     },
            //     {
            //         label: 'Group 2', children: [
            //             {label: 'Option 2.1', value: '1'},
            //             {label: 'Option 2.2', value: '2'},
            //             {label: 'Option 2.3', value: '3', disabled: true}
            //         ]
            //     },
            //     {
            //         label: 'Group 3', children: [
            //             {label: 'Option 2.1', value: '1'},
            //             {label: 'Option 2.2', value: '2'},
            //             {label: 'Option 2.3', value: '3', disabled: true}
            //         ]
            //     },
            //     {
            //         label: 'Group 4', children: data
            //     }
            // ];
            $('#example-multiple-selected').multiselect({
                enableClickableOptGroups: true,
                buttonText: function (options, select) {
                    return 'ENABLE ▼';
                },
                buttonTitle: function (options, select) {
                    return 'Platforms TLG,WEB,VK';
                },
                onDropdownShow: function(event) {
                    $("span.multiselect-selected-text").text('ENABLE ▲');
                },
                onDropdownHide: function(event) {
                    $("span.multiselect-selected-text").text('ENABLE ▼');
                },
                onChange: function (option, checked, select) {
                    if (Array.isArray(option)) {
                        for (let i = 0; i < option.length; i++) {
                            let channelName =  $(option[i]).attr("label").split(' : ')[0].split(' #')[0];
                            let source =  $(option[i]).val().split(' : ')[0];
                            this.enrichExclusions(source, channelName, checked);
                        }
                    } else {
                        let channelName =  $(option).attr("label").split(' : ')[0].split(' #')[0];
                        let source =  $(option).val().split(' : ')[0];
                        this.enrichExclusions(source, channelName, checked);
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
            $('#example-multiple-selected').multiselect('dataprovider', optsources);
            this.isLoaded = true;
        }.bind(this))
    },

    methods: {
        emitFilter: function (){
            this.$emit("emitPlatformFilter", {
                platformFilter: this.exclusions
            });
        },

        enrichExclusions: function (source, channel_name, selected) {
            if (selected) {
                this.removeFromExclusions(source, channel_name);
            } else {
                this.addToExclusions(source, channel_name);
            }
            this.emitFilter();
        },

        addToExclusions: function (source, channel) {
            if (this.exclusions.map(it => it[1] + ":|:" + it[0]).indexOf(channel + ":|:" + source) === -1) {
                this.exclusions.push([source, channel])
            }
        },

        removeFromExclusions: function (source, channel) {
            let index = this.exclusions.map(it => it[1] + ":|:" + it[0]).indexOf(channel + ":|:" + source);
            if (index !== -1) {
                this.exclusions.splice(index, 1);
            }
        }
    }
};


export {filterRunTimePicker}
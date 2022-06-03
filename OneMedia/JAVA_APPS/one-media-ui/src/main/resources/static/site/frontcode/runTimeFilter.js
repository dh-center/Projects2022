let runTimeFilter = {
    template: '\
    <div  class="runtime-content">\
        <div class="container">\
            <div class="row">\
                <div class="col-sm-auto">\
                    Filter Content : \
                </div>\
                <div class="col-sm-auto">\
                    <input type="text" v-model="queryFilter" class="form-control on-hover-outbound my-fonts input-height" placeholder="Collocations in content" aria-label="Recipient\'s username" aria-describedby="basic-addon2">\
                </div>\
            </div>\
            <div class="row">\
                <div class="col-sm-auto" style="margin-top: 25px;">\
                    <label class="form-check-label" for="flexRadioDefault1">\
                        Time Range : \
                    </label>\
                </div>\
                <div class="col-sm-1" style="margin-top: 25px;">\
                    <calendar-picker :time="dateFilter" :range="dateFilter" @emitDateCalendar="setDateFilterRunTime"></calendar-picker>\
                </div>\
            </div>\
            <div class="row">\
                <filter-platform-picker :news="listToShow" @emitPlatformFilter="setPlatformFilter"></filter-platform-picker>\
            </div>\
            <div class = "row">\
                <div class="col-sm-12">\
                    <div class="d-flex justify-content-end">\
                        <button class="btn btn-danger float-right my-btn-two" v-on:click="applyFilter">APPLY</button>\
                    </div>\
                </div>\
            </div>\
        </div>\
    </div>\
    ',

    data: function (){
        return {
            timeFilter: [],
            queryFilter: '',
            platformsFilter: []
        }
    },

    props: {
        dateFilter: {
            type: Array,
            default: () => []
        },
        listToShow: {
            type: Array,
            default: () => []
        }
    },

    methods: {
        setDateFilterRunTime: function (filter) {
            this.timeFilter = filter.filteredTime;
        },

        setPlatformFilter: function (filter){
            this.platformsFilter = filter.platformFilter;
        },

        applyFilter: function (){
            this.$emit("applyRuntimeFilter", {
                platformsFilter: this.platformsFilter,
                timeFilter: this.timeFilter,
                queryFilter: this.queryFilter
            });
        }
    }
}

export {runTimeFilter};
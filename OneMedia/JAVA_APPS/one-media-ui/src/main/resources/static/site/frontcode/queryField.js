const axios = require('axios');

let queryField = {
        template: '\
    <div xmlns="http://www.w3.org/1999/html">\
        <builder-menu v-show="headMenuIsActive  "></builder-menu>\
        <div class="container" :key="indexCleanMainControl" style="margin-top: 120px" >\
            <div  class="container rounded-border">\
                <div class="row">\
                    <br>\
                </div> \
                <div class="row">\
                    <div class="col-lg" v-if="!useBooleanQuery">\
                        <textarea :readonly="mainControlDisabled" class="form-control on-hover-outbound" rows="3" v-model="queryText" placeholder="Please enter your query"></textarea>\
                    </div>\
                    <div  v-if="useBooleanQuery">\
                        <textarea :readonly="mainControlDisabled" class="form-control on-hover-outbound" rows="9" v-model="advancedQuery" placeholder="Advanced query"></textarea>\
                    </div>\
                </div>\
                <div class="row">\
                    <div class="col-sm form-check form-switch"  style="margin-top: 35px; margin-left: 25px">\
                        <input :disabled="mainControlDisabled" class="form-check-input"  type="checkbox" id="flexSwitchCheckDefault" v-model="useBooleanQuery">\
                        <label class="form-check-label" for="flexSwitchCheckDefault" v-if="useBooleanQuery"> &nbsp;Advanced query</label>\
                        <label class="form-check-label" for="flexSwitchCheckDefault" v-if="!useBooleanQuery"> &nbsp;Simple query</label>\
                    </div>\
                    <div class="col-md-auto extra-additional-margin" style="margin-top: 15px;">\
                        <button v-if="!mainControlDisabled" v-on:click="sendQuery" type="button" class="btn btn-danger my-btn-two">\
                            <span v-if="loadingIsActive" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>\
                                FIND\
                        </button>\
                        <button v-if="mainControlDisabled" class="btn btn-secondary" disabled>FIND</button>\
                        <button v-if="mainControlDisabled" class="btn btn-danger my-btn-two" v-on:click="cleanMainControl">&#x21bb;</button>\
                    </div>\
                </div>\
                <div class="row">\
                    <div class="col-sm-auto form-check form-check-inline" style="margin-top: 25px;">\
                       <label class="form-check-label" for="flexRadioDefault1">\
                        Time Unit : \
                        </label>\
                    </div>\
                    <div class="col-sm-auto form-check form-check-inline" style="margin-top: 25px;">\
                        <input class="form-check-input" type="radio" name="inlineRadioOptions" id="inlineRadio1" value="option1" @change="changeTimeUnit(false)" checked>\
                        <label class="form-check-label" for="inlineRadio1">Day</label>\
                    </div>\
                    <div class="col-sm-1 form-check form-check-inline" style="margin-top: 25px;">\
                        <input class="form-check-input" type="radio" name="inlineRadioOptions" id="inlineRadio2" value="option2" @change="changeTimeUnit(true)">\
                        <label class="form-check-label" for="inlineRadio2">Month</label>\
                    </div>\
                </div>\
                <div class="row" style="padding-bottom: 30px">\
                    <div class="col-sm-auto" style="margin-top: 25px;">\
                        <label class="form-check-label" for="flexRadioDefault1">\
                            Time Range : \
                        </label>\
                    </div>\
                    <div class="col-sm-1" style="margin-top: 25px;">\
                        <calendar-picker :enableDefaults="true" :disabled="mainControlDisabled" @emitDateCalendar="setDateFilter"></calendar-picker>\
                    </div>\
                </div>\
                <Modal v-model="alertShown" title="Check that your input valid!">\
                    <h4 class="alert-heading" style="color: red">Be careful about your search!</h4>\
                    <p>{{alertMessage}}</p>\
                    <hr>\
                    <p class="mb-0">If you are not sure what to do, then consult manual !</p>\
                </Modal>\
            </div>\
            <div v-if="dates.length === 0" class="rounded-border-bottom"></div>\
            <transition name="fade">\
                <div  v-if="dates.length !== 0">\
                    <div>\
                        <ul class="nav nav-tabs nav-fill my-nav-tabs">\
                            <li class="nav-item">\
                                <a v-bind:class="[true ? \'my-active-above\' : \'my-not-active-above\']"  class="nav-link nav-tab-my-hover" href="#">RunTime Filter</a>\
                            </li>\
                            <li class="nav-item">\
                                <a v-bind:class="[false ? \'my-active-above\' : \'my-not-active-above\']" class="nav-link nav-tab-my-hover my-not-active-above" href="#">Save</a>\
                            </li>\
                            <li class="nav-item">\
                                <a class="nav-link nav-tab-my-hover my-active-empty" href="#">&nbsp;</a>\
                            </li>\
                            <li class="nav-item">\
                                <a class="nav-link nav-tab-my-hover my-active-empty-last" href="#">&nbsp;</a>\
                            </li>\
                        </ul>\
                    </div>\
                    <run-time-filter @applyRuntimeFilter="applyRuntimeFilter" :listToShow="listToShow" :dateFilter="dateFilter"></run-time-filter>\
                    <div>\
                        <ul class="nav nav-tabs nav-fill my-nav-tabs">\
                            <li class="nav-item"  v-on:click="chooseList">\
                                <a v-bind:class="[listChosen ? \'my-active\' : \'my-not-active\']" class="nav-link nav-tab-my-hover" href="#">Results</a>\
                            </li>\
                            <li class="nav-item" v-on:click="chooseGraphs">\
                                <a v-bind:class="[graphChosen ? \'my-active\' : \'my-not-active\']" class="nav-link nav-tab-my-hover" href="#">Graphs</a>\
                            </li>\
                            <li class="nav-item" v-on:click="chooseTrace">\
                                <a v-bind:class="[traceChosen ? \'my-active\' : \'my-not-active\']" class="nav-link nav-tab-my-hover" href="#">Trace</a>\
                            </li>\
                            <li class="nav-item" v-on:click="chooseStats">\
                                <a v-bind:class="[statsChosen ? \'my-active\' : \'my-not-active\']" class="nav-link nav-tab-my-hover" href="#" tabindex="-1" aria-disabled="true">Stats</a>\
                            </li>\
                        </ul>\
                    </div>\
                </div>\
            </transition>\
            <user-queries @setAdvancedQuery="setAdvancedQuery" v-if="useBooleanQuery && !mainControlDisabled" :jwt="jwt"></user-queries>\
            <div class="container" v-if="chosenGraphs()"  style="margin-top: 100px">\
                <div v-if="dates.length !== 0" class="row" style="text-align: center; color: rgba(0,0,0,0.5);">\
                    <label>News Per Day</label>\
                </div>\
                <div class="row" v-if="dates.length !== 0 & chosenTab==\'graph\'">\
                    <chart-frequency v-on:choose="chooseDateEmit" :key="indexBarChart" v-bind:pointsx="this.dates" v-bind:pointsy="getNewsCounters()" v-bind:pointsc="getColorsStatic(253, 0, 0, 0.2,dates.length)"></chart-frequency>\
                </div>\
                <div class="center-svg row additional-margin" v-if="dates.length !== 0 & chosenTab==\'graph1\'">\
                    <bar-chartd :key="indexBarD3Chart" v-bind:data="getNewsCountersWithDate()" v-bind:queryText="queryText"></bar-chartd> \
                </div> \
                <div v-if="dates.length !== 0" class="container" @mouseover="mouseOver" @mouseleave="mouseLeave" style="margin-top: 70px">\
                    <div class="row" style="margin-top: 100px; text-align: right; color: rgb(0,0,0,0.2);">\
                        <label v-if="showDoughnuts" v-on:click="showDoughnuts=false">&#10060;</label>\
                        <label v-if="!showDoughnuts" v-on:click="showDoughnuts=true">Show Source/Platform &#128065;</label>\
                    </div>\
                    <transition name="fade">\
                    <div v-if="showDoughnuts">\
                        <div class="row" style="text-align: center; color: rgb(0,0,0,0.7);">\
                            <label>Sources</label>\
                        </div>\
                        <div class="row"> \
                            <div class="col-sm-6">\
                                <doughnut-frequency class="doughnut-chart-label"  :key="indexDoughnutChart"  v-bind:specificLabel="specificNewsDayLabel" v-bind:providedTimeUnit="getTimeUnit()" v-bind:colors="getColorsWithStep(75,0,0,1,this.platforms.length)" v-bind:pointsx="this.platformsDay" v-bind:pointsy="this.platformsDayCounter"></doughnut-frequency>\
                            </div>\
                            <div class="col-sm-6">\
                                <doughnut-frequency class="doughnut-chart-label" :key="indexDoughnutChartPlatform" v-bind:providedTimeUnit="\'All\'" v-bind:colors="getColorsWithStep(75,0,0,1,this.platforms.length)" v-bind:pointsx="this.platforms" v-bind:pointsy="getNewsCountersPlatform()"></doughnut-frequency>\
                            </div>\
                        </div>\
                        <div class="row" style="text-align: center; color: rgb(0,0,0,0.5);">\
                            <label>Platforms</label>\
                        </div>\
                        <div :key="indexDoughnutPlatformTotalChart" class="row">\
                            <changeable-doughnut @chosenPlatform="choosePlatform" v-bind:pointsx="this.sources" v-bind:pointsy="getNewsCountersSources()"></changeable-doughnut>\
                        </div>\
                    </div>\
                    </transition>\
                </div>\
            </div>\
            <div class="container" :key="indexDoughnutChart">\
                <div v-if="listToShow.length !== 0 & chosenTab == \'list\'">// TODO GITHUB LIKE ACTIVITY WINDOW HERE</div>\
                <search-results-filter :newsArray="listToShowFiltered" v-if="chosenTab == \'list\'"></search-results-filter>\
                <search-results-filter :newsArray="specificNewsDayFiltered" v-if="chosenTab == \'graph\'" :chosenPlatforms="chosenPlatforms" ></search-results-filter>\
            </div>\
            <div  style=" padding-bottom: 600px;"></div>\
        </div>\
    </div>\
',

        data: function () {
            return {
                queryText: '',
                advancedQuery: "{\n" +
                    "  \"channels_excluded\": [],\n" +
                    "  \"channels_included\": [],\n" +
                    "  \"excluded_terms\": [],\n" +
                    "  \"must_terms\": [],\n" +
                    "  \"should_terms\": []\n" +
                    "}",
                useBooleanQuery: true,
                timeUnitMonth: false,
                showResultList: true,
                listToShow: [],
                dates: [],
                newsPerDay: [],
                newsPerPlatform: [],
                newsPerSource: [],
                specificNewsDay: [],
                specificNewsDaySum: [],
                specificNewsDayList: [],
                sources: [],
                platforms: [],
                platformsDay: [],
                platformsDayCounter: [],
                chosenTab: "list",
                indexBarChart: 1,
                indexDoughnutChart: 1,
                indexCleanMainControl: 1,
                indexDoughnutChartPlatform: 1,
                indexDoughnutPlatformTotalChart: 1,
                indexBarD3Chart: 1,
                maxDate: '',
                headMenuIsActive: true,
                loadingIsActive: false,
                dateFilter: this.getLastMonthBoundaries(),
                alertShown: false,
                alertMessage: "",

                chosenPlatforms: [],
                showDoughnuts: true,
                mainControlDisabled: false,

                currentFilter: {
                    platformsFilter: [],
                    timeFilter: [],
                    queryFilter: ''
                },

                listToShowFiltered: [],
                specificNewsDayFiltered: [],
                jwt: null
            }
        },

        methods: {
            getOrRequestJwt: function () {
                if (this.jwt == null) {
                    return axios({
                        method: 'get',
                        url: '/auth/jwt'
                    }).then(function (jwt) {
                        this.jwt = jwt.data;
                    }.bind(this));
                }
                console.log("jwt: " + this.jwt);
                return Promise.resolve({data: this.jwt});
            },

            choosePlatform: function (elem) {
                console.log("chosen platform: " + elem.chosenPlatform);
                this.chosenPlatforms = elem.chosenPlatform;
            },

            applyRuntimeFilter: function (filter, rerender = true) {
                console.log("filter======================================")
                console.log(filter.platformsFilter);
                console.log(filter.timeFilter);
                console.log(filter.queryFilter);
                console.log("filter======================================")
                this.currentFilter = filter;

                this.listToShowFiltered = this.listToShow;
                this.specificNewsDayFiltered = this.specificNewsDay;

                if (filter.queryFilter.length !== 0) {
                    let query = filter.queryFilter.toLowerCase();
                    this.listToShowFiltered = this.listToShowFiltered.filter((item) => this.toStringItem(item).indexOf(query) !== -1);
                    this.specificNewsDayFiltered = this.specificNewsDayFiltered.filter((item) => this.toStringItem(item).indexOf(query) !== -1);
                }

                if (filter.platformsFilter.length !== 0) {
                    let exclusions = filter.platformsFilter.map(it => it[1] + ":|:" + it[0]);
                    this.listToShowFiltered = this.listToShowFiltered.filter((item) => exclusions.indexOf(item.channelName + ":|:" + item.source) === -1);
                    this.specificNewsDayFiltered = this.specificNewsDayFiltered.filter((item) => exclusions.indexOf(item.channelName + ":|:" + item.source) === -1);
                }

                if (filter.timeFilter.length !== 0 && filter.timeFilter[0] !== null && filter.timeFilter[2] !== null) {
                    let from = this.getUtcDate(filter.timeFilter[0]);
                    let to = this.getUtcDate(filter.timeFilter[1]);
                    this.listToShowFiltered = this.listToShowFiltered
                        .filter((item) => from <= this.getUtcDate(item.publishDate) && this.getUtcDate(item.publishDate) <= to);
                    this.specificNewsDayFiltered = this.specificNewsDayFiltered
                        .filter((item) => from <= this.getUtcDate(item.publishDate) && this.getUtcDate(item.publishDate) <= to);
                }

                this.initialiseData(false);

                if (rerender) {
                    this.reRenderGrapgh();
                    this.reRenderSearch();
                }
            },


            enableAlert: function (message) {
                this.alertMessage = message;
                this.alertShown = true;
            },

            disableAlert: function () {
                this.alertShown = false;
            },

            setDateFilter: function (filter) {
                if (filter.filteredTime.length === 0 || filter.filteredTime[0] === null || filter.filteredTime[2] === null) {
                    this.dateFilter = [];
                    return;
                }
                this.dateFilter = filter.filteredTime;
            },

            chooseDateEmit: function (dateValue) {
                console.log(dateValue);
                let date = dateValue.dateToShow;
                let value = dateValue.valueToShow;

                this.specificNewsDay = this.newsPerDay[date];
                this.specificNewsDaySum = value;
                this.specificNewsDayLabel = date;
                this.applyRuntimeFilter(this.currentFilter, false);
                this.reRenderDoughnutDay()
                this.reRenderSearch();
            },

            refillForSpecificDate: function (dateArr) {
                // platformsDay
                this.platformsDay = dateArr.map(function (item) {
                    return item.channelTitle;
                }).sort().filter((v, i, a) => a.indexOf(v) === i);

                this.platformsDayCounter = [];

                for (let i = 0; i < this.platformsDay.length; i++) {
                    this.platformsDayCounter.push(0);
                }

                for (let i = 0; i < dateArr.length; i++) {
                    this.platformsDayCounter[this.platformsDay.indexOf(dateArr[i].channelTitle)] += 1;
                }
            },

            sendQuery: function () {
                this.getOrRequestJwt().then(
                    function (jwt) {
                        let currJwt = jwt.data;
                        let startDate = null, endDate = null;

                        if (this.dateFilter.length !== 0) {
                            startDate = new Date(this.dateFilter[0]).getTime();
                            endDate = new Date(this.dateFilter[1]).getTime();
                        }

                        if (!this.useBooleanQuery) {
                            if (this.queryText === null || this.queryText.length === 0) {
                                this.enableAlert("Your query text is an empty string!");
                                return;
                            }
                            if (this.queryText.length < 2) {
                                this.enableAlert("Your query text is too small! Text: " + this.queryText);
                                return;
                            }
                        }
                        this.disableAlert();

                        let query = {
                            publishTimeRange: {
                                from: startDate,
                                to: endDate
                            },
                            enrich_content: true,
                            number_of_best_hits: 2000
                        };

                        let queryToRead = {};
                        if (this.useBooleanQuery) {
                            try {
                                queryToRead = JSON.parse(this.advancedQuery);
                            } catch (e) {
                                this.enableAlert("Your query isn't a valid json!")
                                return;
                            }
                            if (queryToRead.must_terms.length === 0) {
                                this.enableAlert("Too broad query!");
                                return;
                            }
                        }
                        this.loadingIsActive = true;
                        if (this.useBooleanQuery) {
                            axios({
                                method: 'post',
                                url: '/userQuery/validateUserQuery',
                                data: {
                                    query: this.advancedQuery
                                }
                            }).then(
                                function (response) {
                                    let sourceMap = function (list) {
                                        return {
                                            source: list[0],
                                            channelName: list[1]
                                        }
                                    };
                                    let termsMap = function (terms) {
                                        return {
                                            synonyms: terms
                                        }
                                    };
                                    query.contentDocTermsMust = queryToRead.must_terms.map(termsMap);
                                    query.contentDocTermsShould = queryToRead.should_terms.map(termsMap);
                                    query.contentDocTermsExcluded = queryToRead.excluded_terms.map(termsMap);

                                    query.channelNamesIncluded = queryToRead.channels_included.map(sourceMap);
                                    query.channelNamesExcluded = queryToRead.channels_excluded.map(sourceMap);
                                    query.sources = queryToRead.hasOwnProperty("sources") ? queryToRead.sources : [];
                                    axios({
                                        method: 'post',
                                        url: 'http://54.36.174.129:8083/search_old',
                                        data: query,
                                        headers: {'X-One-Media': currJwt}
                                    }).then(function (response) {
                                        try {
                                            if (response.data.length === 0) {
                                                this.emptyResponseAlert();
                                                return;
                                            }
                                            for (let i = 0; i < response.data.length; i++) {
                                                response.data[i].publishDate = this.getStringRepresentationOfDateByNum(response.data[i].publishDate);
                                            }
                                            this.listToShow = response.data;
                                            this.listToShowFiltered = this.listToShow;
                                            if (response.data.length === 0) {
                                                this.loadingIsActive = false;
                                                return;
                                            }
                                            this.initialiseData(true);
                                            this.reRenderGrapgh();
                                            this.mainControlDisabled = true;
                                        } finally {
                                            this.loadingIsActive = false;
                                        }
                                    }.bind(this)).catch(
                                        function (error) {
                                            console.log(error)
                                            this.loadingIsActive = false;
                                        }.bind(this)
                                    );
                                }.bind(this)
                            ).catch(
                                function (error) {
                                    console.log(error);
                                    this.loadingIsActive = false;
                                    this.enableAlert("Query isn't correct!");
                                }.bind(this)
                            );
                        } else {
                            query.contentLuceneQuery = this.queryText;

                            axios({
                                method: 'post',
                                url: 'http://54.36.174.129:8083/search_old',
                                data: query,
                                headers: {'X-One-Media': currJwt}
                            }).then(function (response) {
                                try {
                                    if (response.data.length === 0) {
                                        this.emptyResponseAlert();
                                        return;
                                    }
                                    for (let i = 0; i < response.data.length; i++) {
                                        response.data[i].publishDate = this.getStringRepresentationOfDateByNum(response.data[i].publishDate);
                                    }

                                    this.listToShow = response.data;
                                    this.listToShowFiltered = this.listToShow;
                                    if (response.data.length === 0) {
                                        this.loadingIsActive = false;
                                        return;
                                    }
                                    this.initialiseData(true);
                                    this.reRenderGrapgh();
                                    this.mainControlDisabled = true;
                                } finally {
                                    this.loadingIsActive = false;
                                }
                            }.bind(this)).catch(
                                function (error) {
                                    console.log(error)
                                    this.loadingIsActive = false;
                                }.bind(this)
                            );
                        }
                    }.bind(this)
                )
            },

            emptyResponseAlert: function () {
                this.enableAlert("We haven't found news for your query!");
            },

            validateTerms: function (arr) {
                if (arr === '') {
                    return true;
                }
                let parsed = JSON.parse(arr);
                if (!Array.isArray(parsed)) {
                    return false;
                }
                for (let i = 0; i < parsed.length; i++) {
                    if (!Array.isArray(parsed[i])) {
                        return false;
                    }
                    for (let j = 0; j < parsed[i].length; j++) {
                        if (!this.isString(parsed[i][j])) {
                            return false;
                        }
                    }
                }
                return true;
            },

            isString: function (x) {
                return Object.prototype.toString.call(x) === "[object String]"
            },

            setAdvancedQuery: function (query) {
                this.advancedQuery = query.query;
            },

            initialiseData: function (overrideSpecificDate) {
                this.dates = this.getFrequencyLabels(this.listToShow);
                this.newsPerDay = this.getNews(this.listToShowFiltered, this.getDateUnitActive());
                this.newsPerPlatform = this.getNews(this.listToShowFiltered, 'channelTitle');
                this.newsPerSource = this.getNews(this.listToShowFiltered, 'source');

                this.sources = Object.keys(this.newsPerSource);
                this.platforms = Object.keys(this.newsPerPlatform);


                if (overrideSpecificDate) {
                    this.maxDate = this.dates[0];
                    for (let i = 0; i < this.dates.length; i++) {
                        if (this.newsPerDay[this.dates[i]].length > this.newsPerDay[this.maxDate].length) {
                            this.maxDate = this.dates[i];
                        }
                    }

                    this.specificNewsDay = this.newsPerDay[this.maxDate];
                    this.specificNewsDayFiltered = this.specificNewsDay;
                    this.specificNewsDayLabel = this.maxDate;
                }
                this.specificNewsDaySum = this.specificNewsDayFiltered.length;
                this.refillForSpecificDate(this.specificNewsDayFiltered);
            },

            formatterForMonth: function (date) {
                let split = date.split("-");
                let month_number = parseInt(split[1]);
                let year_number = parseInt(split[0].substr(2, 4));

                return year_number + " " + this.getMonthFromNumber(month_number);
            },


            getFrequencyLabels: function (data) {
                if (data.length > 0) {
                    let result = [];

                    for (let i = 0; i < data.length; i++) {
                        if (!('publishDateMonth' in data[i])) {
                            data[i].publishDateMonth = this.formatterForMonth(data[i].publishDate);
                        }
                        let formattedDate = data[i][this.getDateUnitActive()];
                        if (result.indexOf(formattedDate) === -1) {
                            result.push(formattedDate);
                        }
                    }
                    console.log(result);
                    return result.sort();
                }
                return [];
            },

            getDateUnitActive: function () {
                if (this.timeUnitMonth) {
                    return 'publishDateMonth';
                }
                return 'publishDate'
            },

            getNews: function (data, field) {
                let result = [];
                for (let i = 0; i < data.length; i++) {
                    if (data[i][field] in result) {
                        result[data[i][field]].push(data[i]);
                    } else {
                        let temp = [];
                        temp.push(data[i]);
                        result[data[i][field]] = temp;
                    }
                }
                return result;
            },

            getNewsCounters: function () {
                let result = [];
                for (let i = 0; i < this.dates.length; i++) {
                    if (this.dates[i] in this.newsPerDay) {
                        result.push(this.newsPerDay[this.dates[i]].length);
                    } else {
                        result.push(0);
                    }
                }
                return result;
            },

            getNewsCountersWithDate: function () {
                let result = [];
                for (let i = 0; i < this.dates.length; i++) {
                    result.push({
                        value: this.newsPerDay[this.dates[i]].length,
                        date: this.dates[i]
                    });
                }
                return result;
            },

            getNewsCountersPlatform: function () {
                let result = [];
                for (let i = 0; i < this.platforms.length; i++) {
                    result.push(this.newsPerPlatform[this.platforms[i]].length);
                }
                return result;
            },

            getNewsCountersSources: function () {
                let result = [];
                for (let i = 0; i < this.sources.length; i++) {
                    result.push(this.newsPerSource[this.sources[i]].length);
                }
                return result;
            },

            resizeWindow: function () {
                this.reRenderDoughnut();
            },

            cleanMainControl: function () {
                this.queryText = '';
                this.showResultList = true;
                this.listToShow = [];
                this.listToShowFiltered = [];
                this.dates = [];
                this.advancedQuery = "{\n" +
                    "  \"channels_excluded\": [],\n" +
                    "  \"channels_included\": [],\n" +
                    "  \"excluded_terms\": [],\n" +
                    "  \"must_terms\": [],\n" +
                    "  \"should_terms\": []\n" +
                    "}";
                this.newsPerDay = [];
                this.newsPerPlatform = [];
                this.newsPerSource = [];
                this.specificNewsDay = [];
                this.specificNewsDayFiltered = [];
                this.specificNewsDaySum = [];
                this.specificNewsDayList = [];
                this.sources = [];
                this.platforms = [];
                this.platformsDay = [];
                this.platformsDayCounter = [];
                this.chosenTab = "list";
                this.indexBarChart = 1;
                this.indexDoughnutChart = 1;
                this.indexDoughnutChartPlatform = 1;
                this.indexBarD3Chart = 1;
                this.maxDate = '';
                this.headMenuIsActive = true;
                this.loadingIsActive = false;
                this.dateFilter = this.getLastMonthBoundaries();
                this.alertShown = false;
                this.alertMessage = "";

                this.chosenPlatforms = [];
                this.showDoughnuts = true;
                this.mainControlDisabled = false;

                this.indexCleanMainControl += 1;
            },

            // ------------ rerender
            reRenderDoughnut: function () {
                this.indexDoughnutChart += 1;
                this.indexDoughnutChartPlatform += 1;
                this.indexDoughnutPlatformTotalChart += 1;
            },

            reRenderDoughnutDay: function () {
                this.indexDoughnutChart += 1;
            },


            reRenderBarChart: function () {
                this.indexBarChart += 1;
                this.indexBarD3Chart += 1;
            },

            reRenderSearch: function () {
                this.indexDoughnutChart += 1;
            },

            reRenderGrapgh: function () {
                this.reRenderBarChart();
                this.reRenderDoughnut();
            },

            chooseList: function () {
                this.listToShowFiltered = this.listToShow;
                this.chosenTab = "list";
                this.reRenderSearch();
            },

            chooseGraphs: function () {
                if (this.chosenTab == "graph") {
                    return;
                    // this.chosenTab = "graph1";
                } else {
                    this.chosenTab = "graph";
                }
                this.reRenderGrapgh();
            },

            chosenGraphs: function () {
                return this.chosenTab == "graph" | this.chosenTab == "graph1";
            },


            chooseTrace: function () {
                this.chosenTab = "trace";
            },

            chooseStats: function () {
                this.chosenTab = "stats";
            },

            //------------- utils

            getLastMonthBoundaries: function () {
                return [this.getStringRepresentationOfDate(new Date(new Date().getTime() - (31 * 24 * 60 * 60 * 1000))),
                    this.getStringRepresentationOfDate(new Date())]
            },

            getStringRepresentationOfDate: function (date) {
                return date.toISOString().slice(0, 10);
            },

            getStringRepresentationOfDateByNum: function (utcNum) {
                return new Date(utcNum).toISOString().slice(0, 10);
            },

            getMonthFromNumber: function (number) {
                switch (number) {
                    case 1:
                        return "Jan";
                    case 2:
                        return "Feb";
                    case 3:
                        return "March";
                    case 4:
                        return "April";
                    case 5:
                        return "May";
                    case 6:
                        return "June";
                    case 7:
                        return "Jule";
                    case 8:
                        return "Aug";
                    case 9:
                        return "Sep";
                    case 10:
                        return "Oct";
                    case 11:
                        return "Nov";
                    case 12:
                        return "Dec";
                    default:
                        console.log("There isn't such month! " + number);
                }
            },

            changeTimeUnit: function (isMonth) {
                this.timeUnitMonth = isMonth;
                if (this.listToShow.length === 0) {
                    return;
                }
                this.initialiseData(true);
                this.reRenderGrapgh();
                this.reRenderSearch();

                console.log("timeUnit: ");
                console.log(isMonth);
            },

            getTimeUnit: function () {
                return this.timeUnitMonth ? "Month" : "Day";
            },

            mouseOver: function () {
                this.headMenuIsActive = false;
            },

            mouseLeave: function () {
                this.headMenuIsActive = true;
            },

            dynamicColors: function () {
                let r = Math.floor(Math.random() * 255);
                let g = Math.floor(Math.random() * 255);
                let b = Math.floor(Math.random() * 255);
                return "rgb(" + r + "," + g + "," + b + ")";
            },

            getColors: function poolColors(a) {
                let pool = [];
                for (let i = 0; i < a; i++) {
                    pool.push(this.dynamicColors());
                }
                return pool;
            },

            getColorsWithStep: function poolColorsWithStep(r, g, b, step, a) {
                let pool = [];
                for (let i = 0; i < a; i++) {
                    pool.push(this.dynamicColorsWithStep(r, g, b, step * i, i / (a + 1) + 0.1));
                }
                return pool;
            },

            getColorsStatic: function (r, g, b, op, length) {
                let colors = [];
                for (let i = 0; i < length; i++) {
                    colors.push("rgb(" + r + "," + g + "," + b + "," + op + ")");
                }
                return colors;
            },

            dynamicColorsWithStep: function (r, g, b, step, op) {
                return "rgb(" + ((r + step) % 255) + "," + ((g + step) % 255) + "," + ((b + step) % 255) + "," + op + ")";
            },

            toStringItem: function (item) {
                return (item.content + " " + item.channelTitle + " " + item.channelName).toLowerCase();
            },

            getUtcDate: function (dateString) {
                let date = new Date(dateString);
                return date.getTime() + (date.getTimezoneOffset() * 60000);
            },

        },

        created: function () {
            this.getOrRequestJwt();
            window.addEventListener("resize", this.resizeWindow);
        },

        computed: {
            listChosen: function () {
                return this.chosenTab === "list";
            }
            ,
            graphChosen: function () {
                return this.chosenTab === "graph";
            }
            ,
            traceChosen: function () {
                return this.chosenTab === "trace";
            }
            ,
            statsChosen: function () {
                return this.chosenTab === "stats";
            }
            ,
        }
        ,

    }
;


export {queryField};
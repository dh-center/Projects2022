import Vue from "vue";

const axios = require('axios');

let userQuery = {
    template: '\
    <div class="card" style = "margin-top: 20px;" >\
         <div class="card-header user-query" style="background-color:  rgba(232, 203, 203, 0.53)">\
            <div class="row">\
                <div class="col-sm-6">\
                    <strong>Name: <span style="color: rgba(138,2,2,0.93)">{{query.name}}</span> </strong><br/>\
                     &#x1F551; : {{query.createdTime.split(".")[0]}}\
                </div>\
                <div class="col-sm-1">\
                    <a v-if="toggleDesc == false" class="toggle-expand" style="margin-right: 28px" v-on:click="showExpand()"><i class="fas fa-eye"></i></a>\
                    <a v-if="toggleDesc == true" class="toggle-expand" style="margin-right: 28px" v-on:click="showExpand()"><i class="fas fa-eye-slash"></i></a>\
                </div>\
            </div> \
        </div>\
        <div class="card-body my-card-body"  v-if="toggleDesc">\
             <div v-if="isUpdated" class="input-group" style="margin-bottom: 10px">\
                <div class="input-group-prepend">\
                    <span class="on-hover-outbound btn btn-primary my-btn-one input-group-text" id="basic-addon1" v-on:click="addBucket()"><i class="fas fa-plus"></i></span>\
                </div>\
                <input type="text" class="on-hover-outbound form-control" placeholder="bucket of words" aria-label="Input group example" v-model="bucketOfWords">\
                <div class="btn-group mr-2" role="group" aria-label="First group">\
                    <button v-bind:class="{ chosen_btn: typeOfBucketUpdate==\'MUST\' }" type="button" class="on-hover-outbound btn btn-primary my-btn-one input-group-text" v-on:click="typeOfBucketUpdate = \'MUST\'">Must</button>\
                    <button v-bind:class="{ chosen_btn: typeOfBucketUpdate==\'SHOULD\'  }" type="button" class="on-hover-outbound btn btn-primary my-btn-one input-group-text" v-on:click="typeOfBucketUpdate = \'SHOULD\'">Should</button>\
                    <button v-bind:class="{ chosen_btn: typeOfBucketUpdate==\'EXCLUDED\'  }" type="button" class="on-hover-outbound btn btn-primary my-btn-one input-group-text" v-on:click="typeOfBucketUpdate = \'EXCLUDED\'">Excluded</button>\
                </div>\
            </div>\
            <div class="btn-toolbar justify-content-between" role="toolbar" aria-label="Toolbar with button groups">\
                <div v-if="isUpdated" class="btn-group" style="margin-bottom: 10px">\
                    <div class="btn-group mr-2">\
                        <span class="on-hover-outbound btn btn-primary my-btn-one input-group-text" id="basic-addon1" v-on:click="addSourceFiltersBucket"><i class="fas fa-tasks"></i></span>\
                    </div>\
                    <div class="btn-group mr-2" role="group" aria-label="First group">\
                        <button v-bind:class="{ chosen_btn: typeOfSourceUpdate==\'EXCLUDE\' }" type="button" class="on-hover-outbound btn btn-primary my-btn-one input-group-text" v-on:click="changeOfFilterSourceType(\'EXCLUDE\')">Exclude</button>\
                        <button v-bind:class="{ chosen_btn: typeOfSourceUpdate==\'INCLUDE\' }" type="button" class="on-hover-outbound btn btn-primary my-btn-one input-group-text" v-on:click="changeOfFilterSourceType(\'INCLUDE\')">Include</button>\
                    </div>\
                    <button class="on-hover-outbound btn btn-primary my-btn-one input-group-text"><source-filter :title="\'Channels\'" :type="typeOfSourceUpdate" :query="query.query" :name="query.name" :jwt="jwt" @emitChosenFilter="handleEmitChosenFilter" :preSelected="preSelectedSources"></source-filter></button>\
                </div>\
                 <div v-if="isUpdated" class="btn-group" style="margin-bottom: 10px">\
                    <div class="btn-group mr-2" role="group" aria-label="First group">\
                        <button type="button" class="on-hover-outbound btn btn-primary my-btn-one input-group-text"><source-switch-box v-on:emitUpdateSwitchBoxSources="handleEmitUpdateSwitchBoxSources" :preSelected="updatedSources"></source-switch-box></button>\
                    </div>\
                </div>\
            </div>\
            <div class="row">\
                <textarea class="form-control on-hover-outbound" v-model="query.query" rows="11" placeholder="{}" :readonly="!isUpdated"></textarea>\
            </div> \
            <div class="row">\
                <div class="btn-group" v-if="!isCopied" style="margin-top: 10px">\
                    <button type="button" v-if="!isUpdated" class="on-hover-outbound btn btn-primary my-btn-one" v-on:click="startUpdate()"><i class="fas fa-pencil-alt"></i></button>\
                    <button type="button" v-if="!isUpdated" class="on-hover-outbound btn btn-primary my-btn-third" v-on:click="startCopy()"><i class="far fa-copy"></i></button>\
                    <button type="button" v-if="!isUpdated" class="on-hover-outbound btn btn-primary my-btn-second" v-on:click="removeQuery()"><i class="fas fa-trash-alt"></i></button>\
                    <button type="button" v-if="!isUpdated" class="on-hover-outbound btn btn-primary my-btn-fourth" v-on:click="setQuery()"><i class="fas fa-filter"></i></button>\
                    <button type="button" v-if="isUpdated" class="on-hover-outbound btn btn-primary my-btn-one" v-on:click="startCommit()">COMMIT</button>\
                    <button type="button" v-if="isUpdated" class="on-hover-outbound btn btn-primary my-btn-second" v-on:click="startRollback()">ROLLBACK</button>\
                </div> \
                <div v-if="isCopied" class="btn-group" role="group" style = "margin-top: 10px" >\
                    <button type="button" class = "on-hover-outbound btn btn-primary my-btn-one" v-on:click="createCopy()">SUBMIT</button>\
                    <input type="text" class="on-hover-outbound form-control" placeholder="New name" v-model="newName"/>\
                    <button type="button" class="on-hover-outbound btn btn-danger my-btn-two" v-on:click="startCopy()">&#x21bb;</button>\
                </div> \
            </div>\
        </div>\
        <Modal v-model="showModal" title="Check that your input valid!">\
             <div>\
                <a>Terms are incorrect: <span v-for="item in showModalIllegals" class="btn btn-danger">{{item}}</span></a>\
             </div>\
        </Modal>\
    </div>\
    ',

    methods: {

        changeOfFilterSourceType: function (type) {
            this.typeOfSourceUpdate = type;
            let query = JSON.parse(this.query.query);
            switch (type) {
                case "INCLUDE":
                    this.preSelectedSources = query.channels_included;
                    break;
                case "EXCLUDE":
                    this.preSelectedSources = query.channels_excluded;
                    break;
            }
        },

        setQuery: function () {
            this.$emit("setAdvancedQuery", this.query);
        },

        showExpand: function () {
            this.toggleDesc = !this.toggleDesc;
            this.isUpdated = false;
            this.query.query = this.original;
        },

        startUpdate: function () {
            this.isUpdated = !this.isUpdated;
        },

        startCommit: function () {
            this.startUpdate();
            axios({
                method: 'post',
                url: '/userQuery/updateUserQuery',
                data: {
                    userId: this.query.userId,
                    name: this.query.name,
                    query: this.query.query
                },
            }).then(function (response) {
                console.log(response.data);
                this.$emit("updateQueries");
            }.bind(this)).catch(
                function (error) {
                    console.log('Error notification! ' + error)
                    this.query.query = this.original;
                }.bind(this)
            );
        },

        startCopy: function () {
            this.isCopied = !this.isCopied;
        },

        createCopy: function () {
            let newName = this.newName.trim();
            if (newName === "") {
                newName = "unknown " + (new Date()).getTime();
            }
            this.newName = ""
            axios({
                method: 'post',
                url: '/userQuery/userQuery',
                data: {
                    userId: this.query.userId,
                    name: newName,
                    query: this.query.query
                },
            }).then(function (response) {
                console.log(response.data);
                this.$emit("updateQueries");
            }.bind(this));
            this.isCopied = false
        },

        removeQuery: function () {
            axios({
                method: 'post',
                url: '/userQuery/removeUserQuery',
                data: {
                    userId: this.query.userId,
                    name: this.query.name,
                    uid: this.query.uid,
                    query: ""
                },
            }).then(function (response) {
                console.log(response.data);
                this.$emit("updateQueries");
            }.bind(this));
        },

        startRollback: function () {
            this.startUpdate();
            this.query.query = this.original;
            let parsed = JSON.parse(this.original);
            this.updatedSources = parsed.hasOwnProperty("sources") ? parsed.sources : [];
        },

        changeToggle: function (open) {
            this.toggleDesc = open;
        },

        handleEmitChosenFilter: function (event) {
            this.chosenSources = event.chosenSources;
        },

        addBucket: function () {
            let processed = this.bucketOfWords.split(",").map(function (str) {
                return str.trim();
            });
            let illegalTerms = processed.filter(function (str) {
                return str.indexOf(" ") !== -1 || str.indexOf("\"") !== -1;
            });
            this.showModal = illegalTerms.length !== 0;
            this.showModalIllegals = illegalTerms;
            if (!this.showModal) {
                let parsed = JSON.parse(this.query.query);
                switch (this.typeOfBucketUpdate) {
                    case 'MUST':
                        parsed.must_terms.push(processed);
                        break;
                    case 'SHOULD':
                        parsed.should_terms.push(processed);
                        break;
                    case 'EXCLUDED':
                        parsed.excluded_terms.push(processed);
                        break;
                }
                this.query.query = JSON.stringify(parsed, null, 2);
                this.bucketOfWords = '';
            }
        },

        addSourceFiltersBucket: function () {
            let parsed = JSON.parse(this.query.query);
            console.log(this.chosenSources);
            switch (this.typeOfSourceUpdate) {
                case "EXCLUDE":
                    parsed.channels_excluded = this.chosenSources;
                    break;
                case "INCLUDE":
                    parsed.channels_included = this.chosenSources;
                    break;
            }
            this.query.query = JSON.stringify(parsed, null, 2);
        },

        handleEmitUpdateSwitchBoxSources: function (event) {
            this.updatedSources = event.chosen;
            let parsed = JSON.parse(this.query.query);
            parsed.sources = this.updatedSources;
            this.query.query = JSON.stringify(parsed, null, 2);
        },

        initializeSources: function () {
            let parsed = JSON.parse(this.query.query);
            if (parsed.hasOwnProperty("sources")){
                this.updatedSources = parsed.sources;
            }
        }
    },

    data: function () {
        return {
            updatedSources: [],
            newName: '',
            isUpdated: false,
            toggleDesc: false,
            isCopied: false,
            original: '',
            typeOfBucketUpdate: 'MUST',
            typeOfSourceUpdate: 'EXCLUDE',
            chosenSources: [],
            preSelectedSources: [],
            bucketOfWords: '',
            showModal: false,
            showModalIllegals: ''
        }
    },

    props: {
        query: {
            type: Object,
            default: null
        },
        open: {
            type: Boolean,
            default: false
        },
        bus: {
            type: Object,
            default: null
        },
        jwt: {
            type: String
        }
    },

    created: function () {
        this.original = this.query.query;
        this.changeOfFilterSourceType("EXCLUDE");
        this.initializeSources();
    },

    mounted: function () {
        this.bus.$on('changeToggle', this.changeToggle)
    }
}

let userQueries = {
    template: '\
    <div class="row querycontainer" :key="updateKey" style="margin-top: 30px; padding-bottom: 10px" >\
        <div class="btn-toolbar justify-content-between" role="toolbar" style="margin-top: 15px; margin-bottom: 0 !important;">\
            <div class="input-group">\
                <div class="input-group-prepend">\
                    <span v-if="!isLoading" class="on-hover-outbound btn btn-primary my-btn-one input-group-text" id="basic-addon1" style="cursor: default"><i class="fas fa-filter"></i></span>\
                    <button v-if="isLoading" class="on-hover-outbound btn btn-primary my-btn-one input-group-text"><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span></button>\
                </div>\
                <input type="text" class="on-hover-outbound form-control" placeholder="filter ..." aria-label="Input group example" v-model="filterValue">\
            </div>\
            <div class = "btn-group mr-2" role = "group" >\
                <button type="button" class="eye-button" v-on:click="plus()"><i class="toggle-expand-not-absolute fas fa-plus"></i></button>\
                <button type="button" class="eye-button" v-on:click="openAll(true)"><i class="toggle-expand-not-absolute fas fa-eye"></i></button>\
                <button type="button" class="eye-button" v-on:click="openAll(false)"><i class="toggle-expand-not-absolute fas fa-eye-slash"></i></button>\
            </div>\
        </div>\
        <div>\
            <user-query @setAdvancedQuery="setAdvancedQuery" v-if="isShown(item)" @updateQueries="updateQueries" v-for="item in queries" v-bind:bus="bus" v-bind:key="item.id" v-bind:query="item" v-bind:jwt="jwt">\
                {{item.query}}\
            </user-query>\
            <Modal v-model="showModal" title="Choose name">\
                <div class="input-group">\
                <div class="input-group-prepend">\
                    <span class="on-hover-outbound btn btn-primary my-btn-one input-group-text" id="basic-addon1" v-on:click="createNew()"><i class="fas fa-plus"></i></span>\
                </div>\
                <input type="text" class="on-hover-outbound form-control" placeholder="Put new name here ..." aria-label="Input group example" v-model="newName">\
            </div>\
            </Modal>\
        </div>\
    </div>\
    ',

    data: function () {
        return {
            updateKey: 1,
            queries: [],
            bus: new Vue(),
            filterValue: '',
            showModal: false,
            newName: '',
            isLoading: true
        }
    },

    props: {
        userId: {
            type: String,
            default: ''
        },
        jwt: {
            type: String,
            default: ''
        },
    },

    methods: {
        setAdvancedQuery: function (query) {
            this.$emit("setAdvancedQuery", query);
        },

        createNew: function () {
            console.log("new!");
            let newName = this.newName.trim()
            if (newName === '') {
                newName = "unknown " + (new Date()).getTime();
            }
            axios({
                method: 'post',
                url: '/userQuery/userQuery',
                data: {
                    userId: -1,
                    name: newName,
                    query: "{\n" +
                        "  \"channels_excluded\": [],\n" +
                        "  \"channels_included\": [],\n" +
                        "  \"excluded_terms\": [],\n" +
                        "  \"must_terms\": [],\n" +
                        "  \"should_terms\": []\n" +
                        "}"
                },
            }).then(function (response) {
                console.log(response.data);
                this.updateQueries()
            }.bind(this));
            this.showModal = false;
            this.newName = '';
        },

        plus: function () {
            this.showModal = true;
        },

        isShown: function (item) {
            if (this.filterValue.trim() === "") {
                return true;
            }
            let content = item.name + " " + item.query;
            return content.toLowerCase().indexOf(this.filterValue.toLowerCase()) !== -1
        },

        openAll: function (open) {
            this.bus.$emit('changeToggle', open)
        },

        updateQueries: function () {
            this.retrieveQueries()
        },

        retrieveQueries: function () {
            axios({
                method: 'get',
                url: '/userQuery/userQuery',
            }).then(function (response) {
                this.queries = response.data.sort(function (a, b) {
                    if (a.createdTime > b.createdTime) {
                        return -1;
                    }
                    if (a.createdTime < b.createdTime) {
                        return 1;
                    }
                    return 0;
                }).map(function (query) {
                    query.query = JSON.stringify(JSON.parse(query.query), null, 2);
                    return query;
                });
                this.updateKey += 1;
                this.isLoading = false;
                console.log("userQueries updated!")
            }.bind(this));
        }
    },

    created: function () {
        this.retrieveQueries()
    }
}

export {userQuery};
export {userQueries};

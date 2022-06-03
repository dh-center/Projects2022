let adminMenu = {
    template: '<div>\
    <project-switcher @currentProjectName="changeProject" @addWork="addWork"></project-switcher>\
        </br>\
    <admin-entry v-for="work in works" @editWork="editWork" @removeWork="removeWork" v-bind:key="work.workSid" v-bind:work="work"></admin-entry>\
        </br>\
    <work-updater @closeWorkEditor="closeWorkEditor" @refreshUi="refreshUi" v-if="updateWork" v-bind:work="this.workToUpdate" v-bind:newOrUpdate="this.newOrUpdate"></work-updater>\
        </div>',
    data: function(){
        return {
            works: undefined,
            updateWork: false,
            workToUpdate: null,
            newOrUpdate: "",
            currentProjectName: null
        }
    },

    methods: {

        refreshUi: function(){
            this.getCurrentWorks(this.currentProjectName);
        },


        removeWork: function(workId){
            axios({
                method: 'get',
                url: '/rest/removeWork?workId='+workId,
            }).then(function (response) {
                console.log(response.data);
                this.changeProject(this.currentProjectName);
            }.bind(this));
        },

        addWork: function(){
            this.updateWork = true;
            this.workToUpdate = {
                name: "",
                projectName: this.currentProjectName,
                parentName: null,
                workSid: null,
                date: "Today",
                description: "",
                estimatedTime: 0,
                workCompletion: 0,
                isMainScreen: false
            };
            this.newOrUpdate = "new";
        },

        getCurrentWorks : function(projectName){
            axios({
                method: 'post',
                url: '/rest/getWorks',
                data: {projectName},
                responseType: 'json'
            }).then(function (response) {
                console.log(response.data);
                this.works = response.data;
            }.bind(this));
        },

        changeProject : function (projectName) {
            console.log("catched projectName: "+projectName);
            this.currentProjectName = projectName;
            this.updateWork = false;
            this.getCurrentWorks(projectName);
        },

        editWork : function (work) {
            console.log("catched work : "+work.name)
            this.updateWork = true;
            this.workToUpdate = work;
            this.newOrUpdate = "update";
        },

        closeWorkEditor : function () {
            this.updateWork = false;
        }
    },
    created: function () {
        console.log("admin menu created!");
    }
};


export {adminMenu};
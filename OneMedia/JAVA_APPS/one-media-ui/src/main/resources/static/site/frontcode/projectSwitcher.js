let projectSwitcher = {
    template: '<div class="row">\
                <div class="col-4">\
                    <select style="background: rgb(93,255,255)" v-model="currentProjectName">\
                        <option disabled value="">Choose project!</option>\
                        <option v-for="project in projects">{{project.projectName}}</option>\
                    </select>\
                    <button class="btn btn-outline-primary"><i class="fa fa-plus"> Add Project</i></button>\
        </div>\
                <div v-if="this.currentProjectName !== null" class="col-6">\
                  <h4 class="alert-heading">Project : {{ currentProjectName }}</h4>\
                </div>\
                <div v-if="this.currentProjectName !== null" v-on:click="addWork" class="col-2">\
                  <button type="button" style="width: 100px" class="btn btn-outline-primary" \
                  @mouseleave="addWorkText = \'Add Work\'" \
                  @mouseover="addWorkText = \'+\'">{{addWorkText}}</button>\
                </div>\
            </div>',
    data: function () {
        return {
            projects: undefined,
            currentProjectName: null,
            addWorkText: "Add Work"
        }
    },

    methods: {
        addWork : function () {
            this.$emit("addWork");
        }
    },

    watch: {
        currentProjectName: function (val) {
            console.log("emitted currentProjectName: "+this.currentProjectName);
            this.$emit("currentProjectName", this.currentProjectName);
        },
    },
    created: function () {

        axios({
            method: 'get',
            url: '/rest/getProjects',
            responseType: 'json'
        }).then(function (response) {
            this.projects = response.data
        }.bind(this));
    }
};


export {projectSwitcher};
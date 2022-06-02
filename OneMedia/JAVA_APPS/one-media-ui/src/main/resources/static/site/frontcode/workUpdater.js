let workUpdater = {
    template: '\
        <div class="just-padding-far container" style=" border: 2px outset #5d0be36e; border-radius: 10px;">\
        <div class="row">\
            <h2 v-if="newOrUpdate === \'update\'">Update work: <span style="color: rgba(99,92,227,0.43)">{{work.name}}</span></h2>\
            <h2 v-if="newOrUpdate === \'new\'">Add work: <span style="color: rgba(99,92,227,0.43)">{{work.name}}</span></h2>\
        </div>\
        <br>\
        <div class="row">\
        <div class="col-8">\
                <label>Name</label>\
                <input v-model="work.name" type="text" class="form-control">\
                <br>\
                <label>Progress</label>\
                <input v-model="work.workCompletion" type="number" min="1" max="100" class="form-control">\
                <br>\
                <label>Estimated Time</label>\
                <input v-model="work.estimatedTime" type="number" min="1" max="1000" class="form-control">\
                <br>\
                <div  v-if="newOrUpdate === \'new\'">\
                    <label >Parent Name</label>\
                    <select style="background: rgb(93,255,255)" v-model="work.parentName">\
                        <option disabled value="">Choose parent!</option>\
                        <option v-for="workName in worksNames">{{workName}}</option>\
                        <option value="null">Empty</option>\
                    </select>\
                </div>\
                <br>\
                <label>Description</label>\
                <textarea v-model="work.description" style="width: 100%"></textarea>\
                <br>\
                <br>\
                <label>Is main screen job?&nbsp&nbsp</label>\
                <input v-model="work.isMainScreen" type="checkbox">\
        </div>\
        <div class="col-4">\
                <label>Project Name : {{work.projectName}}</label>\
                <br>\
                <label>Date : {{work.date}}</label>\
                <br>\
                <label v-if="newOrUpdate === \'update\'">Parent Name : {{work.parentName}}</label>\
                <br>\
                <label v-if="work.workSid!==null">Work id : {{work.workSid}}</label>\
                <label v-if="work.workSid===null">Work id : <i  class="fa fa-ban"></i></label>\
        </div>\
        <br>\
        <br>\
        <br>\
        </div>\
        <div class="row just-padding" >\
            <div class="col-2">\
                <div class="row">\
                <div class="col-6">\
                    <button v-if="newOrUpdate === \'update\'" :disabled="isUpdating" v-on:click="updateWork" class="btn btn-outline-primary">Update</button>\
                    <button v-if="newOrUpdate === \'new\'" :disabled="isUpdating" v-on:click="addWork" class="btn btn-outline-primary">Add</button>\
                </div>\
                <div class="col-6">\
                    <button v-if="isUpdating" v-on:click="unLockUpdate" class="btn btn-outline-primary"><i  class="fa fa-unlock"></i></button>\
                </div>\
                </div>\
            </div>\
            <div class="col-8">\
            </div>\
            <div class="col-2">\
                <button v-on:click="close" class="btn btn-outline-primary">Close</button>\
            </div>\
        </div>\
        </div>'
    ,

    data: function () {
        return {
            isUpdating: false,
            worksNames: null
        }
    },

    props: {
        work: Object,
        newOrUpdate: String,
    },

    methods: {

        unLockUpdate: function(){
            this.isUpdating = false;
        },

        close: function () {
            this.isUpdating = false;
            this.$emit("closeWorkEditor");
        },

        updateWork: function () {
            this.isUpdating = true;
            axios({
                method: 'post',
                url: '/rest/updateWork',
                data: this.work,
            }).then(function (response) {
                console.log(response.data);
                this.$emit("refreshUi");
            }.bind(this));
        },

        addWork: function () {
            this.isUpdating = true;

            this.work.children = [];
            axios({
                method: 'post',
                url: '/rest/addWork',
                data: this.work,
            }).then(function (response) {
                console.log(response.data);
                this.$emit("refreshUi");
            }.bind(this));
        }
    },


    created: function () {
        if (this.newOrUpdate === 'new') {
            axios({
                method: 'post',
                url: '/rest/getWorksNames',
                data: {projectName : this.work.projectName},
                responseType: 'json'
            }).then(function (response) {
                console.log(response.data);
                this.worksNames = response.data;
            }.bind(this));
        }
    }
};

export {workUpdater};


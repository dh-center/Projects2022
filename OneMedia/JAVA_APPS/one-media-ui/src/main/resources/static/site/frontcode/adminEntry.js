let adminEntry = {
    props: {
        work: Object
    },
    template: '<div class="just-padding-left">\
                <a v-bind:href="\'#item\'+this.work.workSid" class="list-group-item" data-toggle="collapse">\
                <div class="row">\
                 <div  class="col-3"><i v-if="work.children.length > 0" class="fa fa-chevron-right"></i>{{work.name}}</div>\
                 <div class="col-3">{{work.estimatedTime}} h\
                 </div>\
                 <div class="col-4">\
                  <div class="row">\
                   <div class="col-9">\
                    <div class="progress">\
                        <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" v-bind:style="{ width: work.workCompletion + \'%\' }" v-bind:aria-valuenow="work.workCompletion" aria-valuemin="0" aria-valuemax="100">{{work.workCompletion}}%</div>\
                    </div>\
                    </div>\
                 </div>\
                 </div>\
                 <div class="col-2">\
                    <i  v-on:click="editWork(work)" class="fa fa-edit"></i>\
                    &nbsp&nbsp&nbsp<button type="button" class="btn btn-primary">workId : {{work.workSid}}</button>\
                    &nbsp&nbsp&nbsp<i v-on:click="removeWork(work.workSid)" class="fa fa-remove"></i>\
                 </div>\
               </div>\
             </a>\
             <div class="list-group collapse" v-bind:id="\'item\'+this.work.workSid">\
                   <admin-entry @editWork="editWork" @removeWork="removeWork" v-for="workChild in orderedWorksChildren" v-bind:key="workChild.workSid" v-bind:work="workChild">\
                   </admin-entry>\
             </div>\
             </div>',

    methods: {
        editWork : function (work) {
            this.$emit("editWork", work);
        },
        
        removeWork : function (workId) {
            this.$emit("removeWork", workId);
        }
    },

    computed: {
        orderedWorksChildren: function () {
            return _.orderBy(this.work.children, 'workSid');
        }
    },

    created: function () {
        console.log("adminEntry created!" + this.work);
    }
};


export {adminEntry};
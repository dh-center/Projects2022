let navbarResults = {
    template: '\
    <nav class="navbar navbar-light my-navbar-one">\
      <form class="form-inline">\
        <div class="input-group">\
          <div class="input-group-prepend">\
            <span class="on-hover-outbound btn btn-primary my-btn-one input-group-text" id="basic-addon1" v-on:click="filterValues()"><i class="fas fa-filter"></i></span>\
          </div>\
          <input v-on:keyup.enter="filterValues()" type="text" class="on-hover-outbound form-control" placeholder="put your text here ..." aria-label="query" aria-describedby="basic-addon1" v-model="filterText">\
        </div>\
      </form>\
      <a class="navbar-brand" v-if="searchFieldResults !== 0" style="color: rgba(0,0,0,0.4)">#{{searchFieldResults}}</a>\
    </nav>',
    props: {
        searchFieldResults: 0
    },

    data: function (){
        return {
            filterText: "",
        }
    },

    methods: {
        filterValues: function (){
            this.$emit("emitFilterNavBar", {
                filteredText: this.filterText
            });
        }
    }
};

export {navbarResults};
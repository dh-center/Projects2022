let sourceSwitchBox = {
    template: "\
            <div>\
                <select v-bind:id=\"getId()\" multiple=\"multiple\"></select>\
            </div>\
    ",

    props: {
        preSelected: {
            type: Array,
            default: () => []
        },
        title: {
            type: String,
            default: "Sources"
        }
    },

    data: function () {
        return {
            chosen: []
        }
    },

    mounted: function () {
        let optsources = [];
        optsources.push(
            {
                label: "VK",
                selected: this.checkPreSelected("VK")
            }
        );
        optsources.push(
            {
                label: "TLG",
                selected: this.checkPreSelected("TLG")
            }
        );
        optsources.push(
            {
                label: "WEB",
                selected: this.checkPreSelected("WEB")
            }
        )
        for (let i = 0; i < optsources.length; i++) {
            if (optsources[i].selected){
                this.chosen.push(optsources[i].label);
            }
        }
        let selector = $("#" + this.getId());
        selector.multiselect({
            enableClickableOptGroups: true,
            buttonText: function (options, select) {
                return this.title + ' ▼';
            }.bind(this),
            buttonTitle: function (options, select) {
                return 'Sources for TLG,WEB,VK';
            },
            onDropdownShow: function (event) {
                $("#"+ this.getId()).siblings().first().find("span.multiselect-selected-text").text(this.title + ' ▲');
            }.bind(this),
            onDropdownHide: function (event) {
                $("#"+ this.getId()).siblings().first().find("span.multiselect-selected-text").text(this.title + ' ▼');
            }.bind(this),
            onChange: function (option, checked, select) {
                let sourceName = $(option).attr("label");
                this.enrichChosen(sourceName, checked);
            }.bind(this),
            onSelectAll: function () {
                alert('onSelectAll triggered!');
            },
            dropRight: true,
            maxHeight: 400,
            multiple: true
        });
        selector.multiselect('dataprovider', optsources);
    },

    methods: {
        enrichChosen: function (source, checked) {
            if (checked) {
                this.chosen.push(source);
            } else {
                let index = this.chosen.indexOf(source);
                if (index !== -1) {
                    this.chosen.splice(index, 1);
                }
            }
            this.$emit("emitUpdateSwitchBoxSources",{
                chosen: this.chosen.length === 3 ? [] : this.chosen
            });
        },

        checkPreSelected: function (choice) {
            if (this.preSelected.length === 0){
                return true;
            }
            return this.preSelected.map((it) => it.toLowerCase()).indexOf(choice.toLowerCase()) !== -1;
        },

        getId: function () {
            return "just-sources" + this.title.hashCode();
        }
    }
};


export {sourceSwitchBox}
import {doughnutOfFrequency} from "./doughnutOfPlatforms";


let changeableDoughnut = {

    template: '\
               <div :key="keyOfDoughnut">\
                   <doughnut-frequency @chosenElem="emitPlatform"  v-bind:providedTimeUnit="\'Platforms\'" v-bind:animate="false" v-bind:transparentLabels="false" v-bind:colors="colors" v-bind:pointsx="pointsx" v-bind:pointsy="pointsy"></doughnut-frequency>\
               </div>\
               ',
    props: {
        pointsx: Array,
        pointsy: Array,
    },

    data: function() {
        return {
            keyOfDoughnut : 1,
            colors: this.getDefaultColors(),
            chosenIndexs: []
        }
    },

    methods : {
        getDefaultColors: function() {
            return this.getColorsWithStep(200, 10, 10, 10,this.pointsx.length);
        },


        getColorsWithStep: function poolColorsWithStep(r, g, b, step, a) {
                let pool = [];
                for (let i = 0; i < a; i++) {
                    pool.push(this.dynamicColorsWithStep(r, g, b, step * i, i / (a + 1) + 0.1));
                }
                return pool;
        },

        dynamicColorsWithStep: function (r, g, b, step, op) {
                    return "rgb(" + ((r + step) % 255) + "," + ((g + step) % 255) + "," + ((b + step) % 255) + "," + op + ")";
        },

        rerenderDougnut: function() {
              this.keyOfDoughnut += 1;
        },

        emitPlatform: function (elem) {
              let index = elem.chosenElem;

              this.colors = this.getDefaultColors();
              if (this.chosenIndexs.length === 0 || this.chosenIndexs.indexOf(index) === -1){
                    this.chosenIndexs.push(index);
              } else {
                    this.chosenIndexs = this.chosenIndexs.filter(x => x !== index);
              }

              this.chosenIndexs.forEach(function(index) {
                    this.colors[index] = this.dynamicColorsWithStep(20,10,150, index * 20, 0.3);
              }.bind(this));

              this.$emit("chosenPlatform", {
                      chosenPlatform: this.chosenIndexs.map(function(index) {
                            return this.pointsx[index];
                      }.bind(this))
              });
              this.rerenderDougnut();
        },


        resizeWindow: function () {
            this.rerenderDougnut();
        }
    },

     created: function (){
            window.addEventListener("resize", this.resizeWindow);
        }
}

export {changeableDoughnut}
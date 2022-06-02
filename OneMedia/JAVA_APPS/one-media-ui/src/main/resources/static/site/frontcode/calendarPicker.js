import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';


let calendarPicker = {
    components: {DatePicker},

    template: '\
    <div>\
        <date-picker v-model="timeValue"  valueType="format" :disabled-date="disabledRangeChecker" placeholder=" Last Month"  @change="emitDate" :disabled="disabled" class="startDate" range>\
         <template v-if="enableDefaults" v-slot:footer="{ emit }">\
          <div style="text-align: left">\
            <button class="mx-btn mx-btn-text" @click="selectToday(emit)">\
              Today\
            </button>\
          </div>\
          <div style="text-align: left">\
            <button class="mx-btn mx-btn-text" @click="selectLastWeek(emit, 7)">\
              Last Weak\
            </button>\
          </div>\
          <div style="text-align: left">\
            <button class="mx-btn mx-btn-text" @click="selectLastWeek(emit, 31)">\
              Last Month\
            </button>\
          </div>\
          <div style="text-align: left">\
            <button class="mx-btn mx-btn-text" @click="selectLastWeek(emit, 62)">\
              Last Two Months\
            </button>\
          </div>\
          <div style="text-align: left">\
            <button class="mx-btn mx-btn-text" @click="selectLastWeek(emit, 182)">\
              Last Six Months\
            </button>\
          </div>\
          <div style="text-align: left">\
            <button class="mx-btn mx-btn-text" @click="selectLastWeek(emit, 365)">\
              Last Year\
            </button>\
          </div>\
        </template>\
        </date-picker>\
    </div>\
  ',

    data () {
        return {
            timeValue: this.time
        }
    },

    props: {
        time: {
            type: Array,
            default: () => null
        },
        disabled: {
            type: Boolean,
            default: false
        },
        range: {
            type: Array,
            default: () => []
        },
        enableDefaults: {
            type: Boolean,
            default: false
        }
    },

    methods: {
        getMsByDate: function (days) {
            return days * 24 * 3600 * 1000;
        },

        selectToday(emit) {
            const start = new Date();
            const end = new Date();
            const date = [start, end];
            emit(date);
        },

        selectLastWeek(emit, days) {
            const start = new Date();
            const end = new Date();
            start.setTime(start.getTime() - this.getMsByDate(days));
            const date = [start, end];
            emit(date);
        },


        emitDate: function () {
            this.$emit("emitDateCalendar", {
                filteredTime: this.timeValue
            });
        },

        disabledRangeChecker: function (date){
            let time = date.getTime();
            if (this.range.length === 0) {
                return time > this.getUtcDateNow();
            }
            return time < this.getUtcDate(this.range[0]) || time  > this.getUtcDate(this.range[1]) ||  time > this.getUtcDateNow();
        },

        getUtcDate: function (dateString){
            let date = new Date(dateString);
            return date.getTime() + (date.getTimezoneOffset() * 60000);
        },

        getUtcDateNow: function (){
            let date = new Date();
            return date.getTime() + (date.getTimezoneOffset() * 60000);
        }
    },

    mounted() {
        console.log("calendar mounted!");
    }

}

export {calendarPicker}
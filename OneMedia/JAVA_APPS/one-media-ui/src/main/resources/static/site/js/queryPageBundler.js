import Vue from 'vue';
import {queryField} from "../frontcode/queryField";
import {searchResult} from "../frontcode/searchResult";
import {tab,tabs} from "./utilComponents";
import {chartOfFrequency} from "../frontcode/chartOfFrequency";
// import {chartOfFrequencyClean} from "../frontcode/chartOfFrequencyClean";
import {doughnutOfFrequency} from "../frontcode/doughnutOfPlatforms";
import {changeableDoughnut} from "../frontcode/changeableDoughnut";
import {barChart} from "../frontcode/barD3";
import ChartDataLabels from 'chartjs-plugin-datalabels';
import Chart from 'chart.js';

import {builderMenu} from "../frontcode/builderMenu";
import {toggleFun} from "../frontcode/listToggler";
import {calendarPicker} from "../frontcode/calendarPicker";
import {navbarResults} from "../frontcode/navbarResults";
import {searchResultsWithFilter} from "../frontcode/searchResultsWithFilter";
import {userQueries} from "../frontcode/userQueries";
import {userQuery} from "../frontcode/userQueries";
import {filterRunTimePicker} from "../frontcode/filterRunTimePicker";
import {sourceFilter} from "../frontcode/sourcesFilter";
import {sourceSwitchBox} from "../frontcode/sourcesSwitchBox";
import {runTimeFilter} from "../frontcode/runTimeFilter";


import VueModal from '@kouts/vue-modal'
import '@kouts/vue-modal/dist/vue-modal.css'

String.prototype.hashCode = function() {
    var hash = 0, i, chr;
    if (this.length === 0) return hash;
    for (i = 0; i < this.length; i++) {
        chr   = this.charCodeAt(i);
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
};

Chart.pluginService.register({
    afterDraw: function(chart, easingValue) {
        // if (easingValue !== 1) {
        //     return;
        // }
        var width = chart.chart.width,
            height = chart.chart.height,
            ctx = chart.chart.ctx,
            type = chart.config.type;

        if (type == 'doughnut')
        {
            var sum = chart.config.options.totaled;
            var oldFill = ctx.fillStyle;
            var fontSize = ((height - chart.chartArea.top) / 300).toFixed(2);

            ctx.restore();
            ctx.font = fontSize + "em sans-serif";
            ctx.textBaseline = "middle"

            var text = chart.config.options.timeUnit + " " + sum,
                specificLabel = chart.config.options.specificLabel,
                textMetrics = ctx.measureText(specificLabel),
                specificLabelX = Math.round((width - textMetrics.width) / 2),
                textX = Math.round((width - ctx.measureText(text).width) / 2),
                textY = (height + chart.chartArea.top) / 2;

            ctx.fillStyle = chart.config.data.datasets[0].backgroundColor[chart.config.data.length - 1];
            ctx.fillText(text, textX, textY);
            ctx.fillText(specificLabel, specificLabelX, textY +  textMetrics.fontBoundingBoxAscent + textMetrics.fontBoundingBoxDescent);
            ctx.fillStyle = oldFill;
            ctx.save();
        }
    }
});
Chart.plugins.register(ChartDataLabels);

Vue.component('Modal', VueModal)
Vue.component("query-field", queryField);
Vue.component("search-result", searchResult);
Vue.component("tabs", tabs);
Vue.component("tab", tab);
Vue.component("chart-frequency", chartOfFrequency);
Vue.component("doughnut-frequency", doughnutOfFrequency);
Vue.component("changeable-doughnut", changeableDoughnut);
Vue.component("bar-chartd", barChart);
Vue.component("builder-menu", builderMenu);
Vue.component("calendar-picker", calendarPicker);
Vue.component("navbar-result", navbarResults);
Vue.component("filter-platform-picker", filterRunTimePicker);
Vue.component("search-results-filter", searchResultsWithFilter);
Vue.component("user-query", userQuery);
Vue.component("user-queries", userQueries);
Vue.component("run-time-filter", runTimeFilter);
Vue.component("source-filter", sourceFilter);
Vue.component("source-switch-box", sourceSwitchBox);

let app = new Vue({el: '#app'});

console.log("query field loaded " + queryField);


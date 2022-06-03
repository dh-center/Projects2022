import {Doughnut} from 'vue-chartjs'



let doughnutOfFrequency = {
    extends: Doughnut,

    props: {
        pointsx: Array,
        pointsy: Array,
        colors: Array,
        providedTimeUnit: {
            type: String,
            default: 'DAY'
        },
        specificLabel: {
            type: String,
            default: ''
        },
        animate: {
            type: Boolean,
            default: true
        },
        transparentLabels: {
            type: Boolean,
            default: true
        }
    },

    computed: {
        sum: function () {
            return this.pointsy.reduce((x,y) => {return x+y;});
        }
    },

    mounted() {

        this.renderChart(
            {
                labels: this.pointsx,
                datasets: [{
                    label: 'Count per platform',
                    backgroundColor: this.colors,
                    data: this.pointsy,
                    hoverOffset: 4,

                }]
            }, {
              onClick: function (e, items) {
                                let index = items[0]._index;
                                this.$emit("chosenElem", {
                                                chosenElem: index
                                            });
                }.bind(this),
                // tooltips: { to change tooltip in the future
                //     enabled: true,
                //     mode: 'single',
                //     callbacks: {
                //         label: function(tooltipItems, data) {
                //             console.log(tooltipItems);
                //             console.log(data.labels);
                //             return tooltipItems.yLabel + ' €';
                //         }
                //     }
                // },
                timeUnit: this.providedTimeUnit,
                specificLabel: this.specificLabel,
                totaled: this.pointsy.reduce((x,y) => {return x+y;}, 0),
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                animation : {
                    animateRotate : this.animate
                },
                plugins: {
                    datalabels: {
                        display: false,

                        labels: {

                            index: {
                                align: 'end',
                                anchor: 'end',
                                color: function (ctx) {
                                    return ctx.dataset.backgroundColor;
                                },
                                font: {size: 13},
                                formatter: function (value, ctx) {
                                    return value;
                                },
                                offset: 4,
                                opacity: function (ctx) {
                                    var value = ctx.dataset.data[ctx.dataIndex];
                                    return ctx.active ? 1 : 4 *  value/this.sum;
                                }.bind(this)
                            },
                            value: {
                                align: 'bottom',
                                backgroundColor: function(ctx) {
                                    var value = ctx.dataset.data[ctx.dataIndex];
                                    return value > this.sum /30 ? 'white' : null;
                                }.bind(this),
                                opacity: function (ctx) {
                                    if (!this.transparentLabels) {
                                        return 1;
                                    }
                                    var value = ctx.dataset.data[ctx.dataIndex];
                                    return ctx.active ? 1 : 8 * value/this.sum;
                                }.bind(this),
                                borderRadius: 3,
                                anchor: 'center',
                                font: {
                                    color: 'red',
                                    weight: 'bold',
                                    size: '12'
                                },
                                display: function (context) {
                                    return context.dataset.data[context.dataIndex] > this.sum /30;
                                }.bind(this),
                                formatter: (val, ctx) => {
                                    return this.truncateWithContinuation(ctx.chart.data.labels[ctx.dataIndex], 30);
                                },
                            }
                        }
                    }
                }
            })
    },

    methods: {
        truncateWithContinuation: function (str, length) {
            if (str.length <= length) {
                return str;
            }
            return str.substring(length) + "...";
        }
    },
}

export {doughnutOfFrequency}
import {Bar} from 'vue-chartjs'


let chartOfFrequency = {
    extends: Bar,

    props: {
        pointsx: Array,
        pointsy: Array,
        pointsc: Array,
    },


    mounted() {

        let toRerender = function (index) {
            let value = this.pointsy[index];
            let date = this.pointsx[index];

            this.$emit("choose", {
                dateToShow: date,
                valueToShow: value
            });
            return this.pointsc.map((x) => x);
        }.bind(this);

        this.renderChart({
            labels: this.pointsx,
            datasets: [
                {
                    type: 'bar',
                    label: 'Count of news per day',
                    backgroundColor: this.pointsc,
                    data: this.pointsy,
                    borderWidth: 1
                },
                {
                    type: 'line',
                    label: '',
                    data: this.pointsy,
                    borderWidth: 2,
                    tension: 0.4,
                    borderDash: [5,10]
                }
            ],
        }, {
            plugins: {
                datalabels: {
                    color: 'white',
                    display: function (context) {
                        if (context.dataset.type === "line") {
                            return false;
                        }
                        return context.dataset.data[context.dataIndex] >= 4;
                    },
                    font: {
                        weight: 'bold'
                    },
                    formatter: Math.round
                }
            },
            legend: {
                display: false
            },
             scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                },
            maintainAspectRatio: false,
            onClick: function (c, i) {
                let v = i[0]
                this.data.datasets[0].backgroundColor = toRerender(v._index);
                this.data.datasets[0].backgroundColor[v._index] = 'rgba(245,13,13,0.71)';
                this.update();
            }
        })


    }
}

export {chartOfFrequency}
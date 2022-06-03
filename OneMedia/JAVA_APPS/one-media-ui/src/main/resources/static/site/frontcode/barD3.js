import * as d3 from "d3";


let barChart = {
    template: '\
      <div id=\'layout\'>\
          <div id="container">\
            <svg viewBox=\'0 0 1200 700\'></svg>\
          </div>\
      </div>\
      ',

    props: {
        queryText: {
            type: String,
            default: 'nothing'
        },
        timeUnit: {
            type: String,
            default: 'DAYS'
        },
        data: {
            type: Array,
            default: () => {
                return []
            }
        }
    },

    methods: {
        truncateWithContinuation: function (str, length) {
            if (str.length <= length) {
                return str;
            }
            return str.substring(length) + "...";
        }
    },

    mounted() {
        const sample = this.data;

        let max = sample.map((x) => {
            return x.value;
        }).reduce((max, val) => max > val ? max : val);

        const svg = d3.select('svg');
        const svgContainer = d3.select('#container');

        const margin = 80;
        const width = 1200 - 2 * margin;
        const height = 700 - 2 * margin;

        const chart = svg.append('g')
            .attr('transform', `translate(${margin}, ${margin})`);

        const xScale = d3.scaleBand()
            .range([0, width])
            .domain(sample.map((s) => s.date))
            .padding(0.5)


        console.log(max);
        const yScale = d3.scaleLinear()
            .range([height, 0])
            .domain([0, max]);

        // vertical grid lines
        // const makeXLines = () => d3.axisBottom()
        //   .scale(xScale)

        chart.append('g')
            .attr('transform', `translate(0, ${height})`)
            .call(d3.axisBottom(xScale))
            .selectAll("text")
            .attr("y", 0)
            .attr("x", 9)
            .attr("dy", ".35em")
            .attr("transform", "rotate(70)")
            .style("text-anchor", "start");

        chart.append('g')
            .call(d3.axisLeft(yScale));

        // vertical grid lines
        // chart.append('g')
        //   .attr('class', 'grid')
        //   .attr('transform', `translate(0, ${height})`)
        //   .call(makeXLines()
        //     .tickSize(-height, 0, 0)
        //     .tickFormat('')
        //   )


        const makeYLines = () => d3.axisLeft()
            .scale(yScale)

        chart.append('g')
            .attr('class', 'grid')
            .call(makeYLines()
                .tickSize(-width, 0, 0)
                .tickFormat('')
            )

        const barGroups = chart.selectAll()
            .data(sample)
            .enter()
            .append('g')

        barGroups
            .append('rect')
            .attr('class', 'bar')
            .attr('x', (g) => xScale(g.date))
            .attr('y', (g) => yScale(g.value))
            .attr('height', (g) => height - yScale(g.value))
            .attr('width', xScale.bandwidth())
            .on('mouseenter', function (actual, i) {
                d3.selectAll('.value')
                    .attr('opacity', 0)

                d3.select(this)
                    .transition()
                    .duration(300)
                    .attr('opacity', 0.6)
                    .attr('x', (a) => xScale(a.date) - 5)
                    .attr('width', xScale.bandwidth() + 10)

                const y = yScale(i.value)

                let line = chart.append('line')
                    .attr('id', 'limit')
                    .attr('x1', 0)
                    .attr('y1', y)
                    .attr('x2', width)
                    .attr('y2', y)

                barGroups.append('text')
                    .attr('class', 'divergence')
                    .attr('x', (a) => xScale(a.date) + xScale.bandwidth() / 2)
                    .attr('y', (a) => yScale(a.value) + 30)
                    .attr('fill', 'white')
                    .attr('text-anchor', 'middle')
                    .text((a, idx) => {
                        const divergence = (a.value - i.value).toFixed(1)

                        let text = ''
                        if (divergence > 0) text += '+'
                        text += `${divergence}`

                        return idx !== i ? text : '';
                    })

            })
            .on('mouseleave', function () {
                d3.selectAll('.value')
                    .attr('opacity', 1)

                d3.select(this)
                    .transition()
                    .duration(300)
                    .attr('opacity', 1)
                    .attr('x', (a) => xScale(a.date))
                    .attr('width', xScale.bandwidth())

                chart.selectAll('#limit').remove()
                chart.selectAll('.divergence').remove()
            })

        barGroups
            .append('text')
            .attr('class', 'value')
            .attr('x', (a) => xScale(a.date) + xScale.bandwidth() / 2)
            .attr('y', (a) => yScale(a.value) + 30)
            .attr('text-anchor', 'middle')
            .text((a) => `${a.value}`)

        svg
            .append('text')
            .attr('class', 'label')
            .attr('x', -(height / 2) - margin)
            .attr('y', margin / 2.4)
            .attr('transform', 'rotate(-90)')
            .attr('text-anchor', 'middle')
            .text('Frequency')

        svg.append('text')
            .attr('class', 'label')
            .attr('x', width / 2 + margin)
            .attr('y', height + margin * 2.2)
            .attr('text-anchor', 'middle')
            .text(this.timeUnit)

        svg.append('text')
            .attr('class', 'title')
            .attr('x', width / 2 + margin)
            .attr('y', 40)
            .attr('text-anchor', 'middle')
            .text('Distribution for query: ' + this.truncateWithContinuation(this.queryText, 14))

        svg.append('text')
            .attr('class', 'source')
            .attr('x', width - margin / 4)
            .attr('y', height + margin * 2.4)
            .attr('text-anchor', 'start')
            .text('OneMedia')

        console.log("mounted d3bar!")
    }

}


export {barChart}
import { watch } from "vue"
import "./LineChart.scss"
import { Spinner } from "./Spinner"

export const LineChart = {
    props: ["data", "x", "y", "groupby", "time", "ymax"],
    setup(props) {

        let chart = null
        let data = null

        function get_groups() {
            if (!props.groupby) return Array.from({ length: (props.data?.[0]?.length || 1) - 1 }, (_, k) => k + 1)

            const x = Array.from(new Set(props.data.map(x => x[props.groupby])))
            x.sort()
            return x
        }

        function get_series(group) {
            let series
            if (props.groupby) {
                series = props.data.filter(x => x[props.groupby] === group).map(x => ({ x: x[props.x || 0], y: x[props.y || 1] }))
            } else {
                series = props.data.map(x => ({ x: x[0], y: x[group] }))
            }
            series.sort((a, b) => a.x.localeCompare(b.x))
            return series
        }

        function get_data() {
            if (!props.data) return []
            return {
                datasets: get_groups().map(g => ({
                    label: g,
                    data: get_series(g)
                }))
            }
        }

        function init(el) {
            if (!el) {
                if (chart) chart.destroy()
                return
            }
            if (chart) return;

            data = get_data()
            const ctx = el.getContext("2d");
            chart = new Chart(ctx, {
                type: 'line',
                data,
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            max: props.ymax,
                            beginAtZero: true,
                            type: 'linear',
                            ticks: {
                                color: "#6D6E9C",
                                font: {
                                    size: 14,
                                    family: "Inter",
                                    weight: 600,
                                },
                            }
                        },
                        x: {
                            ticks: {
                                autoSkip: true,
                                maxRotation: 0,
                                minRotation: 0,
                                autoSkipPadding: 40,
                                color: "#6D6E9C",
                                font: {
                                    size: 14,
                                    family: "Inter",
                                    weight: 600,
                                },
                            }
                            ,
                            type: 'time',
                        },
                    },
                    animation: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: "right",
                            labels: {
                                font: {
                                    size: 14,
                                    family: "Inter",
                                },
                                color: "#6D6E9C",
                            }
                        },
                    },
                    elements: {
                        point: {
                            radius: 0,
                        },
                        line: {
                            borderWidth: 2,
                            fill: true,
                            // borderColor: "#2D2E83",
                            // backgroundColor: "#2D2E8322",
                        }
                    }
                }
            })
        }

        function update() {
            if (!chart) return;
            chart.data = get_data()
            chart.update()
        }

        watch(props, update)

        return () => {
            if (isNaN(props.data?.length)) return <Spinner />;
            return <canvas style={{ width: "100%", height: "100%" }} ref={init}></canvas>
        }
    }
}
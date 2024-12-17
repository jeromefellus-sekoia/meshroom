
import "./WorldMap.scss"
import world from "./WorldMap.json"
import { onUnmounted } from "vue";

export const WorldMap = {
    props: ["width", "height", "countries"],
    setup(props) {
        let el = null
        let timer = null

        async function init(_el) {
            if (!_el) return;
            if (el) return;
            el = _el

            setImmediate(() => {
                let svg = d3.select(el)
                const { left, right, top, bottom } = svg.node().getBoundingClientRect()
                let width = right - left
                let height = bottom - top
                svg.attr("width", width).attr("height", height)
                const sensitivity = 75

                let projection = d3.geoOrthographic()
                    .scale(250)
                    .center([0, 0])
                    .rotate([0, -30])
                    .translate([width / 2, height / 2])

                const initialScale = projection.scale()
                let path = d3.geoPath().projection(projection)

                let globe = svg.append("circle")
                    .attr("cx", width / 2)
                    .attr("cy", height / 2)
                    .attr("r", initialScale)

                svg.call(d3.drag().on('drag', () => {
                    const rotate = projection.rotate()
                    const k = sensitivity / projection.scale()
                    projection.rotate([
                        rotate[0] + d3.event.dx * k,
                        rotate[1] - d3.event.dy * k
                    ])
                    path = d3.geoPath().projection(projection)
                    svg.selectAll("path").attr("d", path)
                }))
                    .call(d3.zoom().on('zoom', () => {
                        if (d3.event.transform.k > 0.3) {
                            projection.scale(initialScale * d3.event.transform.k)
                            path = d3.geoPath().projection(projection)
                            svg.selectAll("path").attr("d", path)
                            globe.attr("r", projection.scale())
                        }
                        else {
                            d3.event.transform.k = 0.3
                        }
                    }))

                let map = svg.append("g")

                let data = world

                map.append("g")
                    .attr("class", "countries")
                    .selectAll("path")
                    .data(data.features)
                    .enter().append("path")
                    .attr("class", d => "country_" + d.properties.name.replace(" ", "_"))
                    .attr("d", path)
                    .style('stroke-width', 0.3)
                    .style("opacity", 0.8)

                timer = d3.timer(function (elapsed) {
                    const rotate = projection.rotate()
                    const k = sensitivity / projection.scale()
                    projection.rotate([
                        rotate[0] - 1 * k,
                        rotate[1]
                    ])
                    path = d3.geoPath().projection(projection)
                    svg.selectAll("path")
                        .attr("d", path)
                        .style("fill", d => COLOR(props.countries?.[d.id]))
                        .style("stroke", d => COLOR(props.countries?.[d.id]))
                        .style("stroke-width", d => props.countries?.[d.id] > 0 ? 1 : .2)
                }, 100)
            })
        }

        onUnmounted(() => {
            timer?.stop?.()
            el?.replaceChildren()
        })

        return () => {
            return <svg class='worldmap' width={props.width} height={props.height} ref={init}></svg>
        }
    }
}


const COLOR = x => {
    if (x >= 3) return "#FF0000FF"
    if (x >= 2) return "rgba(255, 0, 0, 0.8)"
    if (x >= 1) return "rgba(255, 0, 0, 0.4)"
    return "#2d2e8369"
}
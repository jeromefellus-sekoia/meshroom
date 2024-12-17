import { watch } from "vue";
import countries from "./globe.json"
import './Globe.scss'

export const Globe = {
    props: ["countries"],
    setup(props) {

        let el = null;
        let globe = null;

        let max = 0

        const MAX_ALPHA = 1;
        const MIN_ALPHA = 0.5;

        function COLOR(country) {
            const n = props?.countries?.[country] || 0
            if (!max || !n) return "#0000"
            return `rgba(255,0,0,${(n / max) * (MAX_ALPHA - MIN_ALPHA) + MIN_ALPHA})`
        }

        function init(_el) {
            if (el) return;
            if (!_el) return;
            el = _el

            setImmediate(() => {
                const getVal = feat => feat.properties.GDP_MD_EST / Math.max(1e5, feat.properties.POP_EST);



                globe = window.Globe()
                    .width(el.offsetWidth)
                    .height(el.offsetHeight)
                    .globeImageUrl("https://unpkg.com/three-globe@2.31.0/example/img/earth-blue-marble.jpg")
                    .backgroundColor("#0000")
                    .lineHoverPrecision(0)
                    .polygonsData(countries.features)
                    .polygonAltitude(0.005)
                    .polygonCapColor(({ properties }) => COLOR(properties.WB_A2))
                    .polygonSideColor(({ properties }) => COLOR(properties.WB_A2))
                    .polygonStrokeColor("#FFF3")
                    .polygonLabel(({ properties: d }) => `
                        <b>${d.ADMIN} (${d.WB_A2})</b> <br />
                        Hosts: <i>${props.countries?.[d.WB_A2] || 0}</i>
                    `)
                    .onPolygonHover(hoverD => globe
                        .polygonAltitude(d => d === hoverD ? 0.01 : 0.005)
                    )
                    .polygonsTransitionDuration(300)
                    (el)

                globe.pointOfView({ lat: 32, lng: 20, altitude: 1 })
                globe.controls().autoRotate = true

            })
        }

        function onMouseenter() {
            if (!globe) return;
            globe.controls().autoRotate = false
        }

        function onMouseleave() {
            if (!globe) return;
            globe.controls().autoRotate = true
        }

        watch(() => props.countries, () => {
            if (!globe) return;
            max = Math.max(...Object.values(props.countries || {}))
            globe?.polygonCapColor(({ properties }) => COLOR(properties.WB_A2))
                .polygonSideColor(({ properties }) => COLOR(properties.WB_A2))
        })

        return () => <div class="globe" ref={init} onMouseenter={onMouseenter} onMouseleave={onMouseleave}>
        </div>
    }
}

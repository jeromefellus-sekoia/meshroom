import CodeMirror from "codemirror";
import "codemirror/lib/codemirror.css";
import "codemirror/theme/midnight.css";
import "codemirror/mode/yaml/yaml";
import './Code.scss'
import { watch, watchEffect } from "vue";

export const Code = {
    props: ["value", "oninput", "readonly", "highlight"],
    setup(props) {

        let codemirror = null

        function init(el) {
            if (!el) return;
            if (codemirror) return;
            setImmediate(() => {
                codemirror = CodeMirror(el, {
                    value: props.value,
                    mode: "yaml",
                    theme: "midnight",
                    lineNumbers: true,
                    smartIndent: true,
                    readOnly: props.readonly,
                    lineWrapping: true,
                })
                codemirror.on("change", () => {
                    props.oninput?.({ target: { value: codemirror.getValue() } })
                })
                setImmediate(highlight)
            })
        }

        function highlight() {
            if (!props.highlight || !codemirror) return;
            codemirror.getAllMarks().forEach(marker => marker.clear());
            props.value.split("\n").forEach((line, i) => {
                let j = 0
                while (j < line.length) {
                    j = line.indexOf(props.highlight, j)
                    if (j === -1 || j >= line.length)
                        break
                    codemirror?.markText({ line: i, ch: j }, { line: i, ch: j + props.highlight.length }, { readOnly: true, className: 'highlighted' })
                    j += props.highlight.length
                }
            })
        }

        watch(() => props.highlight, highlight)
        watch(() => props.value, () => {
            if (codemirror && codemirror.getValue() != props.value) {
                codemirror.setValue(props.value)
                highlight()
            }
        })

        return () => {
            return <div ref={init} />
        }
    }
}
import { watch } from 'vue'
import { debounce } from '../utils'
import './SearchInput.scss'

export const SearchInput = {
    props: ["left", "right", "autofocus", "placeholder", "debounce", "value", "onChange", "clearOnChange"],
    setup(props) {

        const _onChange = debounce(props.onChange, props.debounce)
        let el = null
        function init(_el) {
            if (el || !_el) return
            el = _el
            el.value = props.value || ""

        }

        watch(() => props.value, () => el && (el.value = props.value || ""))

        return () => {
            const { left, right, value, debounce, onChange, ...rest } = props
            return <div class="search-input">
                <div class="left">{left}</div>
                <input ref={init} {...rest}
                    onInput={e => {
                        props?.onInput?.(e)
                        if (props.debounce) {
                            _onChange?.(e.target.value)
                        }
                    }}
                    onKeydown={e => {
                        if (!props.debounce && e.key === "Enter") {
                            onChange?.(e.target.value)
                            if (props.clearOnChange) e.target.value = ""
                        }
                    }} />
                <div class="right">{right}</div>
            </div>
        }
    }
}
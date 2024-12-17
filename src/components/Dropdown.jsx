import { reactive, watchEffect } from 'vue'
import './Dropdown.scss'
import { CONTEXT_MENU, contextMenu } from './ContextMenu'
import { Button } from './Button'
import { ICON } from '../icons'

export const Dropdown = {
    props: ["button", "populate", "onSelect", "combo", "render", "menu"],
    setup(props) {
        let btn = null
        const data = reactive({})

        watchEffect(async () => {
            data.items = await props?.populate?.() || []
        })

        function open(e) {
            const { button, ...rest } = props
            contextMenu(btn || e.target, () => <Dropdown {...rest} />)
            e.stopPropagation(); e.preventDefault()
        }


        return () => {
            if (props.button) {
                return <Button ref={el => btn = el} class="btn-dropdown" onClick={open}>{props.button} {ICON("expand_more")}</Button>
            }

            return <div class="dropdown-menu">
                {props.combo && <input autofocus
                    ref={e => e?.focus()}
                    onClick={e => { e.preventDefault(); e.stopPropagation() }}
                    onKeydown={e => {
                        if (e.key == "Enter") {
                            props.onSelect?.(data.input)
                            CONTEXT_MENU.contextMenu = null;
                        }
                    }}
                    onInput={e => data.input = e.target.value}
                    value={data.input}
                ></input>}
                {props.menu?.()}
                {data.items?.map(item => <DropdownItem onClick={() => props.onSelect?.(item)}>{props.render ? props.render(item) : item}</DropdownItem>)}
            </div>
        }
    }
}

export const DropdownItem = ({ checked }, { slots }) => <div class="item">
    {checked && <>{ICON("check")} &nbsp;</>}
    {slots?.default?.()}
</div>
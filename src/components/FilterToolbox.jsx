import { reactive } from 'vue'
import { ICON } from '../icons'
import './FilterToolbox.scss'
import { ToolButton } from './ToolButton'
import { ToolDropdown } from './ToolDropdown'

export const FilterToolbox = {
    props: ["search", "onSearch", "menu"],
    setup(props) {
        const data = reactive({ search: props.search })
        return () => {
            return <div class="filter-toolbox" class={{ searching: props.search || data.open }} >
                {props.onSearch && <>
                    <ToolButton class="btn-search" onClick={() => data.open = true}>{ICON("search")}</ToolButton>
                    <input value={data.search} onInput={e => data.search = e.target.value} onChange={e => props.onSearch?.(e.target.value)} />
                    <ToolButton class="close-search" onClick={() => { props.onSearch?.(""); data.open = false }}>{ICON("close")}</ToolButton>
                </>}
                {props.menu && <ToolDropdown menuClass="filter-toolbox-menu" icon={ICON("filter_list")} menu={props.menu} />}
            </div >
        }
    }
}
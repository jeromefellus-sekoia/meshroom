import { contextMenu } from "./ContextMenu"
import { ToolButton } from "./ToolButton"
import { Dropdown } from "./Dropdown"
import './ToolDropdown.scss'

export const ToolDropdown = {
    props: ["populate", "icon", "onSelect", "combo", "menu", "menuClass"],
    setup(props) {
        return () => {
            const { icon, ...rest } = props
            return <ToolButton class="tool-dropdown" onClick={(e) => contextMenu(e, <Dropdown class="tool-dropdown-menu" class={props.menuClass} {...rest} />)}>{props.icon}</ToolButton>
        }
    }
}
import { ICON } from '../icons'
import './Badge.scss'
import { ToolButton } from './ToolButton'

export const Badge = ({ color, ...props }, { slots }) => <span class="badge" {...props} style={{ background: color }}>
    {slots?.default?.()}
    {props.onDelete && <ToolButton onClick={props.onDelete}>{ICON("clear")}</ToolButton>}
</span>
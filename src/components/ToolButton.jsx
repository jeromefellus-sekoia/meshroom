import './ToolButton.scss'

export const ToolButton = ({ right, left, ...props }, { slots }) => <button class="toolbutton" {...props}
    style={{ float: right ? "right" : left ? "left" : undefined }}
>
    {slots?.default?.()}
</button>
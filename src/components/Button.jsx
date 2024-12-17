import './Button.scss'

export const Button = ({ secondary, right, left, ...props }, { slots }) => <button {...props}
    class={{ secondary }}
    style={{ float: right ? "right" : left ? "left" : undefined }}
>
    {slots?.default?.()}</button>
import './Callout.scss'

export const Callout = ({ icon, ...props }, { slots }) => <p class="callout" {...props}>
    {icon}
    {slots?.default?.()}
</p>
import './Form.scss'

export const Form = (props, { slots }) => <form
    class="form"
    onSubmit={e => { e.preventDefault(); e.stopPropagation() }}
    {...props}
>
    {slots?.default?.()}
</form>
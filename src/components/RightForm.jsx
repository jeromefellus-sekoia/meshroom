import "./RightForm.scss"

export const RightForm = (props, { slots }) => <div class="right-form">
    {slots?.default?.()}
</div>
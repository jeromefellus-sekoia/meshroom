import './Field.scss'

export const Field = ({ title, cols, ...props }, { slots }) => <div class="field" {...props} style={cols && { gridColumn: `span ${cols}` }}>
    <label>{title}</label>
    {slots?.default?.()}
</div>
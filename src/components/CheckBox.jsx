import './CheckBox.scss'
export const CheckBox = ({ value, onClick }, { slots }) => <div class="form-check" onClickCapture={e => { e.stopPropagation(); e.preventDefault(); onClick?.(e); }}>
    <input class="form-check-input" type="checkbox" value={!!value} checked={!!value} />
    <label class="form-check-label" >
        {slots?.default?.()}
    </label>
</div >
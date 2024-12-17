import './Palette.scss'

export const Palette = {
    setup(props, { slots }) {
        return () => <div class='palette'>
            {slots?.default?.()}
        </div>
    }
}
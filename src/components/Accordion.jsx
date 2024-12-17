import "./Accordion.scss"

export const Accordion = {
    setup(props, { slots }) {
        return () => <div class='accordion'>
            {slots?.default?.()}
        </div>
    },

    Folder: ({ title }, { slots }) => <div class="folder">
        <h3>{title}</h3>
        <div>
            {slots?.default?.()}
        </div>
    </div>,
    Item: (_, { slots }) => <div class="item">{slots?.default?.()}</div>
}

import './Breadcrumb.scss'

export const Breadcrumb = ({ items }) => <div class="breadcrumb">{items?.filter(x => !!x)?.map(x => <>
    &nbsp;&gt;&nbsp;
    {ENTRY(x)}
</>)}
</div>


function ENTRY(x) {
    if (!x) return;
    if (Array.isArray(x)) {
        const [text, href] = x
        if (href) return <a href={href}>{text}</a>
        return { text }
    }
    return x
}
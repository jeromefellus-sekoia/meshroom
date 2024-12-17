import { reactive, watch } from "vue"
import { ICON } from "../icons"
import { UI } from "../main"
import "./DataTable.scss"
import { ToolButton } from "./ToolButton"

export const DataTable = {
    props: ["data", "columns", "empty", "rowClass", "onPageChange", "showTotal", "onExpand", "onCollapse", "expanded", "nopagination", "onRowClick", "isExpanded"],
    setup(props) {
        const state = reactive({ expanded: {} })

        const onPageChange = props.onPageChange || (p => {
            UI.queryParams.page = p
        })

        watch(() => props.data?.page, () => state.expanded = {})

        function toggleExpand(i, x) {
            if (state.expanded[i]) props.onCollapse?.(x)
            else props.onExpand?.(x)
            state.expanded[i] = !state.expanded[i]
        }

        return () => {
            const { data, columns, rowClass, showTotal = true } = props
            const items = data?.items || data

            return <div class="datatable">
                <table>
                    {columns?.filter(c => c.title)?.length > 0 && <thead>
                        <tr>
                            {props.onExpand && <th width={1}></th>}
                            {columns?.map(c => <th width={c.width}>{c.title}</th>)}
                        </tr>
                    </thead>}
                    <tbody>
                        {items?.map((x, i) => <><tr class={typeof rowClass === "function" ? rowClass?.(x) : rowClass} class={{ clickable: !!props?.onRowClick }} onClick={() => props?.onRowClick?.(x)}>
                            {props.onExpand && <th width={1}>
                                <ToolButton onClick={() => toggleExpand(i, x)}>
                                    {ICON(state.expanded[i] ? "expand_more" : "chevron_right")}
                                </ToolButton>
                            </th>}
                            {columns?.map(c => {
                                const s = c.render ? c.render(x) : c[x]
                                return <td width={c.width} class={{ ellipsis: c.ellipsis }} title={c.tooltip?.(x) || c.ellipsis && s}>{s}</td>
                            })}
                        </tr>
                            {(state.expanded[i] || props.isExpanded?.(x)) && <tr class="expanded">
                                <td colSpan={(columns?.length || 0) + 1}>
                                    {props.expanded?.(x)}
                                </td>
                            </tr>}
                        </>)}
                    </tbody>
                </table>

                {!items?.length > 0 && <div class='empty'>{props.empty || "No data"}</div>}
                <div class="spacer" />
                {props?.nopagination ? false : PAGINATION(data, onPageChange, showTotal)}
            </div>
        }
    }
}


export function PAGINATION(data, onPageChange, showTotal = true) {
    let { page, pages, total, length } = data || {}
    if (isNaN(total) && isNaN(length)) return false
    page ||= 1

    const out = []
    if (!isNaN(total) && pages > 0) {
        for (let p = Math.max(page - 3 + 1, 3); p <= Math.min(page + 3 - 1, pages); p++) out.push(p)
        if (out[0] >= 5) out.splice(0, 0, "...")
        if (out[out.length - 1] <= pages - 5) out.push("...")
        for (let p = Math.min(3, pages); p >= 1; p--) {
            if (!out.includes(p)) out.splice(0, 0, p)
        }
        for (let p = Math.max(1, pages - 3 + 1); p <= pages; p++) {
            if (!out.includes(p)) out.push(p)
        }
    }
    return (out.length > 1 || showTotal) && <div class="pagination">
        {out.length > 1 && <>
            <b>page</b>
            <ToolButton onClick={() => onPageChange(page - 1)} disabled={page <= 1}>{ICON("chevron_left")}</ToolButton>
            {out.map(p => p === "..." ? p : <a href="#" class={{ active: p === page }} onClick={() => onPageChange(p)}>{p}</a>)}
            <ToolButton onClick={() => onPageChange(page + 1)} disabled={page >= pages}>{ICON("chevron_right")}</ToolButton>
        </>}
        {showTotal && <><b>total</b> <div class="kpi">{total || length || 0}</div></>}
    </div>
}

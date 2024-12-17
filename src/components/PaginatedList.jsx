import { Badge } from "./Badge"
import "./PaginatedList.scss"

export const PaginatedList = ({ total }, { slots }) => {
    return <div class="paginated-list">
        {slots?.default?.()}
        {[1, 2, 3, "...", 55, 56, 57].map(i => <Badge>{i}</Badge>)}
    </div>
}
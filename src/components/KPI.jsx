import { Badge } from "./Badge"
import "./KPI.scss"

export const KPI = ({ color }, { slots }) => <Badge color={color} class='kpi'>{slots?.default?.()}</Badge>
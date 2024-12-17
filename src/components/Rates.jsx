import { ICON } from '../icons'
import { Badge } from './Badge'
import './Rates.scss'

export const RATES = (produced = 0, consumed = 0) => <div class="rates">
    <Badge class={{ zero: !produced }}>{ICON("upload")} {(produced || 0).toFixed(1)}/s</Badge>
    <Badge class={{ zero: !consumed }}>{ICON("get_app")} {(consumed || 0).toFixed(1)}/s</Badge>
</div>
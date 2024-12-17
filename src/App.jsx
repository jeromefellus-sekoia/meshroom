import { UI } from "./main"
import { ContextMenu, CONTEXT_MENU } from "./components/ContextMenu"
import { LeftPanel } from "./components/LeftPanel"
import { Menu } from "./components/Menu"
import { ICON } from "./icons"
import { RightPanel } from "./components/RightPanel"
import { Button } from "./components/Button"
import { Compose } from "./views/Compose"
import { Play } from "./views/Play"
import { Integrate } from "./views/Integrate"
import { Publish } from "./views/Publish"
import { Toasts } from "./components/Toasts"
import { TopPanel } from "./components/TopPanel"
import { Avatar } from "./components/Avatar"
import { BottomPanel } from "./components/BottomPanel"
import { Palette } from "./components/Palette"
import { Accordion } from "./components/Accordion"

export const ROUTES = [
    { path: "/compose", component: Compose },
    { path: "/play", component: Play },
    { path: "/integrate", component: Integrate },
    { path: "/publish", component: Publish },
    { path: '/:pathMatch(.*)*', redirect: "/compose" }
]


export const App = {
    setup() {
        UI.loading = true
        UI.leftPanelSmall = localStorage.getItem("leftPanelSmall") === "true"

        function toggleLeftPanel() {
            UI.leftPanelSmall = !UI.leftPanelSmall
            localStorage.setItem("leftPanelSmall", UI.leftPanelSmall ? "true" : undefined)
        }

        return () => {
            return <>
                {UI.loading && <div class="loading" />}

                <div id="wrapper">

                    <LeftPanel class={{ small: UI.leftPanelSmall }}>
                        <header>
                            <img class='logo' src='/assets/logo.jpg' />
                        </header>
                        <Button id="collapseLeftPanel" onClick={toggleLeftPanel}>{ICON(UI.leftPanelSmall ? "chevron_right" : "chevron_left")}</Button>
                        <Menu>
                            <Menu.Item icon={ICON("scatter_plot")} to="/compose">Compose</Menu.Item>
                            <Menu.Item icon={ICON("play_arrow")} to="/play">Play</Menu.Item>
                            <Menu.Item icon={ICON("extension")} to="/integrate">Integrate</Menu.Item>
                            <Menu.Item icon={ICON("backup")} to="/publish">Publish</Menu.Item>
                        </Menu>
                    </LeftPanel>

                    <Palette>
                        <Accordion>
                            <Accordion.Folder title={<>{ICON('add')}Add product</>}>
                                {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(_ => <Accordion.Item><img src="https://github.com/SEKOIA-IO/intake-formats/blob/main/HarfangLab/harfanglab/_meta/logo.png?raw=true" />Harfang lab</Accordion.Item>)}
                            </Accordion.Folder>
                            <Accordion.Folder title={<>{ICON('add')}Add integration</>}>
                            </Accordion.Folder>
                        </Accordion>
                    </Palette>

                    <TopPanel class={{ "frame": !!UI.user }}>
                        {UI.user ? <Avatar username={UI.user?.name} image={UI.user?.image} /> : <Button>{ICON("github")} Sign-in via Github</Button>}
                    </TopPanel>


                    <BottomPanel>
                        <Button>{ICON("add")} Add product</Button>
                        <Button>{ICON("add")} Add integration</Button>
                    </BottomPanel>

                    <main>
                        <router-view />

                        {UI.rightPanel && <RightPanel>{UI.rightPanel()}</RightPanel>}
                    </main>
                </div>

                {CONTEXT_MENU.contextMenu?.node && <ContextMenu />}

                <Toasts />
            </>
        }
    }
}

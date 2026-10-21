import type { ReactNode } from 'react'
import { Outlet, createRootRoute, HeadContent, Scripts } from '@tanstack/react-router'
import '../style.css'

export const Route = createRootRoute({
  head: () => ({ meta: [
    { charSet: 'utf-8' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    { title: 'Loop Workbench | Evidence-first Agent Systems' },
    { name: 'description', content: 'Source-bound, read-only Agent loop and RL environment inspection.' },
  ] }),
  component: Root,
})

function Root() {
  return <html lang="zh-Hant">
    <head><HeadContent /></head>
    <body><Outlet /><Scripts /></body>
  </html>
}

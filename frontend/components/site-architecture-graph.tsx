'use client'

import { memo, useCallback, useEffect, useMemo, useState } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  BackgroundVariant,
  type Node,
  type Edge,
  type NodeTypes,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type { GraphNode as GNode, GraphResponse, PageResult } from '@/lib/types'
import { fetchGraph } from '@/lib/api'

// ── Node data ─────────────────────────────────────────────────────────────────

interface SeoNodeData extends Record<string, unknown> {
  label: string
  score: number
  inlinks_count: number
  is_orphan: boolean
  url: string
}

type SeoFlowNode = Node<SeoNodeData>

// ── Layout constants ──────────────────────────────────────────────────────────

const NODE_W = 210
const COL_GAP = 230
const ROW_GAP = 110
const MAX_PER_ROW = 12

function scoreColor(score: number): string {
  if (score >= 70) return '#10b981'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

// ── Custom node ───────────────────────────────────────────────────────────────

function SeoNodeInner({
  data,
  selected,
}: {
  data: SeoNodeData
  selected: boolean
}) {
  const color = scoreColor(data.score)
  return (
    <div
      style={{
        border: `2px ${data.is_orphan ? 'dashed' : 'solid'} ${color}`,
        borderRadius: 8,
        background: selected ? '#27272a' : '#18181b',
        padding: '7px 10px',
        width: NODE_W,
        cursor: 'pointer',
        boxShadow: selected ? `0 0 0 3px ${color}40` : 'none',
        transition: 'box-shadow 0.15s',
      }}
    >
      <Handle type="target" position={Position.Top} style={{ opacity: 0, pointerEvents: 'none' }} />
      <p
        style={{
          fontSize: 11,
          color: '#a1a1aa',
          fontFamily: 'monospace',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          marginBottom: 4,
        }}
      >
        {data.label || '/'}
      </p>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
        <span style={{ color, fontWeight: 700 }}>{data.score}</span>
        {data.inlinks_count > 0 && (
          <span style={{ color: '#71717a' }}>↖ {data.inlinks_count}</span>
        )}
        {data.is_orphan && (
          <span style={{ color: '#78716c', fontSize: 10, marginLeft: 'auto' }}>bağlantısız</span>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0, pointerEvents: 'none' }} />
    </div>
  )
}

const SeoNode = memo(
  (props: { data: SeoNodeData; selected: boolean; [key: string]: unknown }) => (
    <SeoNodeInner data={props.data} selected={props.selected ?? false} />
  )
)
SeoNode.displayName = 'SeoNode'

const NODE_TYPES: NodeTypes = { seoNode: SeoNode as NodeTypes[string] }

// ── Layout builder ────────────────────────────────────────────────────────────

function buildLayout(graphNodes: GNode[]): SeoFlowNode[] {
  const depthMap = new Map<number, GNode[]>()
  const orphans: GNode[] = []

  for (const n of graphNodes) {
    if (n.is_orphan) {
      orphans.push(n)
    } else {
      const arr = depthMap.get(n.click_depth) ?? []
      arr.push(n)
      depthMap.set(n.click_depth, arr)
    }
  }

  const result: SeoFlowNode[] = []
  const depths = [...depthMap.keys()].sort((a, b) => a - b)
  let currentY = 0

  for (const depth of depths) {
    const nodes = depthMap.get(depth)!
    for (let rowStart = 0; rowStart < nodes.length; rowStart += MAX_PER_ROW) {
      const row = nodes.slice(rowStart, rowStart + MAX_PER_ROW)
      const totalWidth = (row.length - 1) * COL_GAP
      row.forEach((n, i) => {
        result.push({
          id: n.id,
          type: 'seoNode',
          position: { x: i * COL_GAP - totalWidth / 2, y: currentY },
          data: {
            label: n.url.replace(/^https?:\/\/[^/]+/, '') || '/',
            score: n.score,
            inlinks_count: n.inlinks_count,
            is_orphan: false,
            url: n.url,
          },
        })
      })
      currentY += ROW_GAP
    }
  }

  if (orphans.length > 0) {
    currentY += ROW_GAP
    for (let rowStart = 0; rowStart < orphans.length; rowStart += MAX_PER_ROW) {
      const row = orphans.slice(rowStart, rowStart + MAX_PER_ROW)
      const totalWidth = (row.length - 1) * COL_GAP
      row.forEach((n, i) => {
        result.push({
          id: n.id,
          type: 'seoNode',
          position: { x: i * COL_GAP - totalWidth / 2, y: currentY },
          data: {
            label: n.url.replace(/^https?:\/\/[^/]+/, '') || '/',
            score: n.score,
            inlinks_count: n.inlinks_count,
            is_orphan: true,
            url: n.url,
          },
        })
      })
      currentY += ROW_GAP
    }
  }

  return result
}

// ── Main component ────────────────────────────────────────────────────────────

interface Props {
  jobId: string
  pages: PageResult[]
  onSelectPage: (page: PageResult) => void
}

export function SiteArchitectureGraph({ jobId, pages, onSelectPage }: Props) {
  const [graph, setGraph] = useState<GraphResponse | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const [nodes, setNodes, onNodesChange] = useNodesState<SeoFlowNode>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])

  const pageMap = useMemo(() => {
    const m = new Map<string, PageResult>()
    for (const p of pages) m.set(p.url, p)
    return m
  }, [pages])

  useEffect(() => {
    setLoading(true)
    setLoadError(null)
    fetchGraph(jobId)
      .then((g) => {
        setGraph(g)
        setNodes(buildLayout(g.nodes))
        setEdges(
          g.edges.map((e) => ({
            id: `${e.source}->${e.target}`,
            source: e.source,
            target: e.target,
            style: { stroke: '#3f3f46', strokeWidth: 1 },
            animated: false,
          }))
        )
      })
      .catch((e: Error) => setLoadError(e.message))
      .finally(() => setLoading(false))
  }, [jobId, setNodes, setEdges])

  const handleNodeClick = useCallback(
    (_evt: React.MouseEvent, node: SeoFlowNode) => {
      const page = pageMap.get(node.id)
      if (page) onSelectPage(page)
    },
    [pageMap, onSelectPage]
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-zinc-600">
        <div className="w-4 h-4 border-2 border-zinc-700 border-t-zinc-400 rounded-full animate-spin mr-3" />
        <span className="text-sm">Graf yükleniyor…</span>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="bg-red-500/8 border border-red-500/20 rounded-xl p-5">
        <p className="text-sm text-red-400">{loadError}</p>
      </div>
    )
  }

  if (!graph) return null

  const orphanCount = graph.nodes.filter((n) => n.is_orphan).length

  return (
    <div className="space-y-3">
      {/* Stats bar */}
      <div className="flex flex-wrap gap-4 text-xs text-zinc-500">
        <span>{graph.nodes.length} düğüm</span>
        <span>{graph.edges.length} kenar</span>
        {orphanCount > 0 && (
          <span className="text-amber-500/80">{orphanCount} bağlantısız sayfa</span>
        )}
        <span className="text-zinc-600">· düğüme tıkla → detay panel</span>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs">
        {[
          { color: '#10b981', label: 'İyi (≥70)' },
          { color: '#f59e0b', label: 'Orta (40–69)' },
          { color: '#ef4444', label: 'Zayıf (<40)' },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <span
              style={{
                display: 'inline-block',
                width: 10,
                height: 10,
                borderRadius: 2,
                background: color,
              }}
            />
            <span className="text-zinc-500">{label}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5">
          <span
            style={{
              display: 'inline-block',
              width: 10,
              height: 10,
              borderRadius: 2,
              border: '2px dashed #71717a',
            }}
          />
          <span className="text-zinc-500">Bağlantısız</span>
        </div>
      </div>

      {/* Graph canvas */}
      <div
        style={{ height: 580, borderRadius: 12, overflow: 'hidden', border: '1px solid #27272a' }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={handleNodeClick}
          nodeTypes={NODE_TYPES}
          fitView
          fitViewOptions={{ padding: 0.15 }}
          minZoom={0.05}
          maxZoom={2}
          attributionPosition="bottom-right"
          style={{ background: '#09090b' }}
        >
          <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#27272a" />
          <Controls style={{ background: '#18181b', border: '1px solid #3f3f46' }} />
          <MiniMap
            style={{ background: '#18181b', border: '1px solid #3f3f46' }}
            maskColor="#09090b88"
            nodeColor={(n) => scoreColor((n.data as SeoNodeData).score)}
          />
        </ReactFlow>
      </div>
    </div>
  )
}

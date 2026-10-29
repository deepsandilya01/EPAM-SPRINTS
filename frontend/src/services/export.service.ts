import { toPng } from 'html-to-image'
import { ScenarioGraph, TraversalResult } from '@/types'

export async function exportGraphToPng(elementId = 'graph-canvas-container', filename = 'intellitwin-graph.png'): Promise<boolean> {
  const node = document.getElementById(elementId)
  if (!node) {
    console.error(`Export error: element #${elementId} not found`)
    return false
  }

  try {
    const dataUrl = await toPng(node, {
      backgroundColor: '#ffffff',
      quality: 0.95,
      filter: (domNode) => {
        // Exclude elements marked for export omission (e.g. interactive controls)
        if (domNode instanceof HTMLElement && domNode.classList.contains('export-ignore')) {
          return false
        }
        return true
      },
    })
    const link = document.createElement('a')
    link.download = filename
    link.href = dataUrl
    link.click()
    return true
  } catch (error) {
    console.error('Failed to export graph to PNG', error)
    return false
  }
}

export function exportGraphDataToCsv(
  graph: ScenarioGraph,
  traversalResult: TraversalResult,
  filename = 'intellitwin-export.csv'
): void {
  const reachedSet = new Set(traversalResult.allReachedNodeIds)

  const headers = [
    'Node ID',
    'Entity Type',
    'Name',
    'Status',
    'Is Source',
    'Is Reached',
    'Details',
  ]

  const rows = graph.nodes.map((node) => {
    const isSource = node.id === traversalResult.sourceNodeId
    const isReached = reachedSet.has(node.id)
    const status = isReached ? 'AFFECTED' : 'UNAFFECTED'

    let detailsStr = ''
    if ('location' in node.details) {
      detailsStr = `Location: ${node.details.location}, Type: ${node.details.type}`
    } else if ('stockLevel' in node.details) {
      detailsStr = `Stock: ${node.details.stockLevel}, Cost: $${node.details.unitCost}`
    } else if ('sku' in node.details) {
      detailsStr = `SKU: ${node.details.sku}, Inv: ${node.details.currentInventory}`
    } else if ('customerName' in node.details) {
      detailsStr = `Customer: ${node.details.customerName}, Qty: ${node.details.quantity}`
    }

    return [
      `"${node.id}"`,
      `"${node.type}"`,
      `"${'name' in node.details ? node.details.name : ('customerName' in node.details ? node.details.customerName : node.id)}"`,
      `"${status}"`,
      `"${isSource}"`,
      `"${isReached}"`,
      `"${detailsStr.replace(/"/g, '""')}"`,
    ].join(',')
  })

  // Append directed edge relationships to CSV output
  const edgeHeaders = ['', '', '', '', '', '', '']
  const edgeSectionTitle = ['--- Graph Directed Edges ---', '', '', '', '', '', '']
  const edgeCols = ['Edge ID', 'Source', 'Target', 'Relation', 'Is Affected', '', '']
  const edgeRows = graph.edges.map((edge) => [
    `"${edge.id}"`,
    `"${edge.source}"`,
    `"${edge.target}"`,
    `"${edge.relation}"`,
    `"${traversalResult.traversedEdgeIds.includes(edge.id)}"`,
    '',
    '',
  ].join(','))

  const csvContent = [
    headers.join(','),
    ...rows,
    edgeHeaders.join(','),
    edgeSectionTitle.join(','),
    edgeCols.join(','),
    ...edgeRows,
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
